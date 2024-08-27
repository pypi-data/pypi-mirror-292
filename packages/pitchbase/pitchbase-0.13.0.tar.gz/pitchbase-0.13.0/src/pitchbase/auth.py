import requests
import os
from .config import Config
from . import constants


class Auth:
    def __init__(
        self,
        config_path: str = constants.DEFAULT_CONFIG_PATH,
        config_profile: str = constants.DEFAULT_CONFIG_PROFILE,
        endpoint: str = None,
        organization_code: str = None,
        username: str = None,
        password: str = None,
        grant_type: str = None,
    ):
        if username is not None:
            self.config = Config(
                {
                    "endpoint": endpoint,
                    "organization_code": organization_code,
                    "username": username,
                    "password": password,
                    "grant_type": grant_type,
                }
            )
        elif os.environ.get("PITCHBASE_USERNAME") is not None:
            self.config = Config(
                {
                    "endpoint": os.environ.get("PITCHBASE_ENDPOINT"),
                    "organization_code": os.environ.get("PITCHBASE_ORGANIZATION_CODE"),
                    "username": os.environ.get("PITCHBASE_USERNAME"),
                    "password": os.environ.get("PITCHBASE_PASSWORD"),
                    "grant_type": os.environ.get("PITCHBASE_GRANT_TYPE"),
                }
            )
        elif config_path is not None:
            self.config = Config.read(config_path, config_profile)
        else:
            raise Exception("Unable to authenticate")

        self.api_url_base = (
            f"https://{self.config.endpoint}/apiv1/{self.config.organization_code}"
        )
        self.session = requests.Session()

    def get_access_token(self, reset: bool = False) -> str:
        if os.environ.get("PITCHBASE_API_TOKEN") is not None and (not reset):
            return os.environ.get("PITCHBASE_API_TOKEN")

        rs = self.session.post(
            f"{self.api_url_base}/auth",
            data={
                "username": self.config.username,
                "password": self.config.password,
                "grant_type": self.config.grant_type,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        return rs.json()["access_token"]

    def get_header(self) -> dict:
        return {
            "X-PitchBase-API-Token": self.get_access_token(),
            "Accept": "application/json",
        }

    def get_api_url_base(self) -> str:
        return self.api_url_base

    def get_session(self) -> requests.Session:
        return self.session
