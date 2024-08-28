import base64
import requests

from dhuolib.config import logger
from dhuolib.services import ServiceAPIMLFacade
from dhuolib.utils import validate_name


class DhuolibPlatformClient:
    def __init__(self, service_uri=None, project_name=None, token=None):
        if not service_uri:
            raise ValueError("service_uri is required")
        if not token:
            raise ValueError("token is required")

        self.service = ServiceAPIMLFacade(service_uri, token=token)
        self.project_name = project_name

    def create_batch_project(self, project_name: str):
        if project_name:
            project_name = validate_name(project_name)
        else:
            project_name = validate_name(self.project_name)

        try:
            response = self.service.project_api.create_project(project_name)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}
        if response.status_code == 400:
            raise ValueError("Project already exists")
        elif response.status_code == 404:
            return ConnectionError("Connection error")

        return response.json()

    def deploy_batch_project(
        self,
        project_name: str = "",
        script_filename: str = "",
        requirements_filename: str = "",
    ):

        if not project_name:
            project_name = self.project_name

        if not project_name:
            raise ValueError("Batch project is required")

        if not (script_filename or requirements_filename):
            raise ValueError("script_filename and requirements_filename are required")

        try:
            with open(script_filename, "rb") as script_file, open(
                requirements_filename, "rb"
            ) as requirements_file:
                encoded_script = base64.b64encode(script_file.read())
                encoded_requirements = base64.b64encode(requirements_file.read())
                try:
                    response = self.service.project_api.deploy_script(
                        project_name=project_name,
                        script_file_encode=encoded_script,
                        requirements_file_enconde=encoded_requirements,
                    )
                except requests.exceptions.HTTPError as e:
                    logger.error(f"Error: {e}")
                    return {"error": str(e)}
                return response
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

    def pipeline_status_report(self, project_name: str = ""):
        lst = []

        if not project_name:
            project_name = self.project_name

        if not project_name:
            raise ValueError("Batch project is required")
        response = self.service.project_api.get_pipeline_status(project_name)

        if "data" in response.keys():
            for data in response["data"]:
                lst.append(
                    {
                        "date_log": data["date_log"],
                        "step": data["step"],
                        "status": data["status"],
                    }
                )
            return lst

        return response

    def create_cluster(self, project_name: str = "", cluster_size: int = 1):

        if not project_name:
            project_name = self.project_name

        if not project_name:
            raise ValueError("Batch project is required")

        if cluster_size not in [1, 2, 3]:
            raise ValueError("cluster_size must be 1, 2 or 3")

        try:
            response = self.service.project_api.create_cluster(
                project_name, cluster_size
            )
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}
        return response

    def batch_run(self, project_name: str = ""):
        if not project_name:
            project_name = self.project_name

        if not project_name:
            raise ValueError("Batch project is required")

        try:
            response = self.service.project_api.run_pipeline(project_name)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}
        return response

    def schedule_batch_run(self, project_name: str = "", schedule_interval: str = ""):
        if not project_name:
            project_name = self.project_name

        if not project_name:
            raise ValueError("Batch project is required")

        try:
            response = self.service.project_api.create_schedule(
                project_name, schedule_interval
            )
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}
        return response

    def remove_schedule(self, project_name: str = ""):
        if not project_name:
            project_name = self.project_name

        if not project_name:
            raise ValueError("Batch project is required")

        try:
            response = self.service.project_api.remove_schedule(project_name)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}
        return response
