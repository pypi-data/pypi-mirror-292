import json
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import Float, Integer, create_engine, inspect, text
from sqlalchemy.dialects.oracle import FLOAT as OracleFLOAT
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import VARCHAR

from dhuolib.config import logger


class DatabaseConnection:
    def __init__(self, config_file_name=None):
        if self.in_dataflow():
            self.connection_string = f"oracle+oracledb://{sys.argv[1]}"
        else:
            f = open(config_file_name)
            data = json.load(f)
            self.connection_string = data["connection_string"]

        self.engine = self._get_engine(self.connection_string)
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def in_dataflow(self):
        if str(Path.home()) == "/home/dataflow":
            return True
        return False

    def _get_engine(self, connection_string):
        self.engine = create_engine(connection_string)
        return self.engine

    @contextmanager
    def session_scope(self, expire=False):
        self.session.expire_on_commit = expire
        try:
            yield self.session
            logger.info(f"Sessão foi iniciada {self.session}")
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro na sessão {self.session}: {e}")
            raise
        finally:
            self.session.close()
            logger.info(f"Sessão foi finalizada {self.session}")


class GenericRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def map_dtype(self, df, engine):
        dtype_mapping = {}
        for col, dtype in df.dtypes.items():
            if pd.api.types.is_integer_dtype(dtype):
                dtype_mapping[col] = Integer()
            elif pd.api.types.is_float_dtype(dtype):
                if engine.dialect.name == "oracle":
                    dtype_mapping[col] = Float(precision=53).with_variant(
                        OracleFLOAT(binary_precision=53), "oracle"
                    )
                else:
                    dtype_mapping[col] = Float()
            elif dtype == "object":
                dtype_mapping[col] = VARCHAR(255)
            else:
                dtype_mapping[col] = VARCHAR(255)
        return dtype_mapping

    def create_table_by_dataframe(self, table_name: str, df: pd.DataFrame):
        if not table_name or df.empty:
            raise ValueError("table_name or data is required")

        with self.db.session_scope() as session:
            inspector = inspect(session.bind)
            if table_name in inspector.get_table_names():
                return f"A tabela {table_name} já existe. Utilize o método update_table_by_dataframe para atualizar a tabela."

            dtype_mapping = self.map_dtype(df, session.bind)

            num_rows_inserted = df.to_sql(
                name=table_name,
                con=session.bind,
                if_exists="replace",
                index=False,
                dtype=dtype_mapping,
            )

        return {"number_lines_inserted": num_rows_inserted, "table_name": table_name}

    # replace_or_append tabela na base de dados
    def update_table_by_dataframe(
        self,
        table_name: str,
        dataframe: pd.DataFrame,
        if_exists: str = "append",
        is_update_version: bool = False,
        force_replace_delete_itens_in_table: bool = False,
    ):
        if if_exists not in ["replace", "append"]:
            raise ValueError("if_exists must be 'append' or 'replace'")

        if not force_replace_delete_itens_in_table and if_exists == "replace":
            confirmation = input(
                "Você tem certeza que deseja fazer a substituição de todos os dados da tabela? Essa operação uma vez escolhida não pode ser desfeita (yes/no): "
            )
            if confirmation.lower() != "yes":
                print("Operação cancelada.")
                return

        if not table_name or dataframe.empty:
            raise ValueError("table_name, dataframe are required")
        with self.db.session_scope() as session:
            if is_update_version:
                df = pd.read_sql(
                    f"SELECT version FROM {table_name.lower()}", con=session.bind
                )
                latest_version = df["version"].max()
                if pd.isna(latest_version):
                    latest_version = 1
                else:
                    latest_version = int(latest_version) + 1

                dataframe["version"] = latest_version
                dataframe["created_at"] = datetime.now()

                dataframe["created_at"] = pd.to_datetime(dataframe["created_at"])

            if if_exists == "replace":
                session.execute(text(f"DELETE FROM {table_name}"))
                dataframe.to_sql(
                    name=table_name, con=session.bind, if_exists="append", index=False
                )
            else:
                dataframe.to_sql(
                    name=table_name, con=session.bind, if_exists="append", index=False
                )

    def to_dataframe(
        self,
        table_name: str = None,
        filter_clause: str = None,
        list_columns: list = None,
        chunksize: int = 10000
    ):
        if not table_name:
            raise ValueError("table_name and list_columns are required")

        columns = ""
        query = ""

        if list_columns:
            columns = ", ".join([column for column in list_columns])
        else:
            columns = "*"

        if filter_clause:
            query = f"SELECT {columns} FROM {table_name} WHERE {filter_clause}"
        else:
            query = f"SELECT {columns} FROM {table_name}"

        df_chunks = []

        with self.db.session_scope() as session:
            for chunk in pd.read_sql(query, con=session.bind, chunksize=chunksize):
                df_chunks.append(chunk)

        df = pd.concat(df_chunks, ignore_index=True)

        return df
