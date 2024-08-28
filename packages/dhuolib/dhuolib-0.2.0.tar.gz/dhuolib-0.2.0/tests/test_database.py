import sys
import unittest

import pandas as pd
from sqlalchemy import text

from dhuolib.repository import DatabaseConnection, GenericRepository

sys.path.append("src")


class TestDatabaseConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_file_name = "tests/files/database.json"
        cls.db_connection = DatabaseConnection(config_file_name=cls.config_file_name)

    def test_database_connection_init(self):
        db_connection = DatabaseConnection(self.config_file_name)
        self.assertIsNotNone(db_connection.engine)
        self.assertIsNotNone(db_connection.session)

    def test_session_scope(self):
        with self.db_connection.session_scope() as session:
            self.assertIsNotNone(session)


class TestGenericRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_file_name = "tests/files/database.json"
        cls.db_connection = DatabaseConnection(config_file_name=cls.config_file_name)
        cls.table_name = "test_table"
        cls.repo = GenericRepository(db_connection=cls.db_connection)
        cls.repo.db.session.execute(
            text(
                f"CREATE TABLE IF NOT EXISTS {cls.table_name} (id INTEGER PRIMARY KEY, name VARCHAR(255), age INTEGER, predict VARCHAR(255), version VARCHAR(255), created_at TIMESTAMP)"
            )
        )

    @classmethod
    def tearDownClass(cls):
        with cls.db_connection.session_scope() as session:
            session.execute(text(f"DROP TABLE IF EXISTS {cls.table_name}"))

    def setUp(self):
        self.db_connection = self.__class__.db_connection
        self.repo = self.__class__.repo
        self.table_name = self.__class__.table_name

    def tearDown(self):
        with self.db_connection.session_scope() as session:
            session.execute(text(f"DELETE FROM {self.table_name}"))

    def test_1_update_table_by_dataframe(self):
        initial_data = pd.DataFrame(
            [{"id": 1, "name": "John Doe", "age": 30, "predict": "Positive"}]
        )
        self.repo.update_table_by_dataframe(
            table_name=self.table_name,
            dataframe=initial_data,
            if_exists="append",
            is_update_version=True,
        )

        new_data = pd.DataFrame(
            [
                {
                    "id": 2,
                    "name": "Jane Doe",
                    "age": 25,
                    "predict": "Positive",
                    "version": 1,
                    "created_at": "2021-01-01",
                },
                {
                    "id": 3,
                    "name": "Jim Beam",
                    "age": 35,
                    "predict": "Negative",
                    "version": 1,
                    "created_at": "2021-01-01",
                },
            ]
        )
        self.repo.update_table_by_dataframe(self.table_name, new_data)

        df = self.repo.to_dataframe(self.table_name)
        self.assertEqual(len(df), 3)
        self.assertListEqual(list(df["name"]), ["John Doe", "Jane Doe", "Jim Beam"])
        self.assertListEqual(list(df["predict"]), ["Positive", "Positive", "Negative"])

    def test_2_create_table_by_dataframe(self):
        with self.db_connection.session_scope() as session:
            session.execute(text(f"DROP TABLE IF EXISTS {self.table_name}"))
        data = pd.DataFrame(
            [
                {
                    "id": 1,
                    "name": "John Doe",
                    "age": 30,
                    "predict": "Positive",
                    "score": 0.932,
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "age": 25,
                    "predict": "Negative",
                    "score": 0.1332,
                },
                {
                    "id": 3,
                    "name": "Bob Johnson",
                    "age": 35,
                    "predict": "Positive",
                    "score": 0.53,
                },
            ]
        )
        self.repo.create_table_by_dataframe(self.table_name, data)
        with self.repo.db.session_scope() as session:
            result = session.execute(
                text(f"SELECT * FROM {self.table_name}")
            ).fetchall()
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0].name, "John Doe")
            self.assertEqual(result[1].name, "Jane Smith")
            self.assertEqual(result[2].name, "Bob Johnson")

    def test_3_update_table_by_dataframe_with_versioning(self):
        with self.repo.db.session_scope() as session:
            session.execute(text(f"DROP TABLE {self.table_name}"))
        data = pd.DataFrame(
            [
                {
                    "id": 1,
                    "name": "John Doe",
                    "age": 30,
                    "predict": "",
                    "created_at": "2021-01-01",
                    "version": 1,
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "age": 25,
                    "predict": "",
                    "created_at": "2021-01-01",
                    "version": 1,
                },
                {
                    "id": 3,
                    "name": "Bob Johnson",
                    "age": 35,
                    "created_at": "2021-01-01",
                    "version": 1,
                    "predict": "",
                },
            ]
        )
        response = self.repo.create_table_by_dataframe(self.table_name, data)
        self.assertEqual(response["number_lines_inserted"], 3)

        update_data = pd.DataFrame(
            [
                {"id": 1, "name": "John Doe", "age": 30, "predict": "Positive"},
                {"id": 2, "name": "Jane Smith", "age": 25, "predict": "Positive"},
                {"id": 3, "name": "Bob Johnson", "age": 35, "predict": "Negative"},
            ]
        )

        self.repo.update_table_by_dataframe(
            table_name=self.table_name,
            dataframe=update_data,
            if_exists="append",
            is_update_version=True,
        )

        df = self.repo.to_dataframe(self.table_name)
        self.assertListEqual(
            list(df["name"]),
            [
                "John Doe",
                "Jane Smith",
                "Bob Johnson",
                "John Doe",
                "Jane Smith",
                "Bob Johnson",
            ],
        )
        self.assertListEqual(
            list(df["predict"]), ["", "", "", "Positive", "Positive", "Negative"]
        )
        self.assertListEqual(list(df["version"]), [1, 1, 1, 2, 2, 2])

    def test_4_to_dataframe_with_chunks_sqlite(self):
        table_name = "test_chunk_table"
        data = pd.DataFrame(
            [
                {"id": 1, "name": "John Doe", "age": 30, "predict": "Positive",
                    "version": 1, "created_at": "2021-01-01"},
                {"id": 2, "name": "Jane Smith", "age": 25, "predict": "Negative",
                    "version": 1, "created_at": "2021-01-01"},
                {"id": 3, "name": "Bob Johnson", "age": 35, "predict": "Positive",
                    "version": 1, "created_at": "2021-01-01"},
                {"id": 4, "name": "Alice Brown", "age": 28, "predict": "Negative",
                    "version": 1, "created_at": "2021-01-01"},
                {"id": 5, "name": "Charlie Davis", "age": 40, "predict": "Positive",
                    "version": 1, "created_at": "2021-01-01"},
                {"id": 6, "name": "Emily Clark", "age": 22, "predict": "Negative",
                    "version": 1, "created_at": "2021-01-01"},
            ]
        )

        print(self.repo.create_table_by_dataframe(table_name, data))

        df = self.repo.to_dataframe(table_name, chunksize=2)

        self.assertEqual(len(df), 6)

        self.assertListEqual(
            list(df["name"]),
            ["John Doe", "Jane Smith", "Bob Johnson",
                "Alice Brown", "Charlie Davis", "Emily Clark"]
        )

        self.repo.db.session.execute(text(f"DROP TABLE {table_name}"))
