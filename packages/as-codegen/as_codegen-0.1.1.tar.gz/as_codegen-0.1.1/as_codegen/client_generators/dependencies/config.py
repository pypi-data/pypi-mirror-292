import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Dict, Optional
from warnings import warn

import toml

ALPHASENSE_KEY = "alphasense"


class ConfigFileNotFound(Exception):
    """Config file not found."""


class InvalidConfiguration(Exception):
    """Configuration not valid."""


class MissingConfiguration(Exception):
    """Configuration not present."""


@dataclass
class BaseConfig:
    url: str = "https://api.alpha-sense.com"
    auth_endpoint: str = "/auth"
    graphql_schema_endpoint: str = "/gql/client-sdk/schema"
    api_endpoint: str = "/gql"

    def __post_init__(self):
        self._set_url()
        self._set_auth_endpoint()
        self._set_graphql_schema_endpoint()
        self._set_api_endpoint()

    def _set_url(self):
        if not self.url:
            self.url = os.environ.get("ALPHASENSE_API_URL")
            if not self.url:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_API_URL'} or 'url' config not found."
                )

    def _set_auth_endpoint(self):
        if not self.auth_endpoint:
            self.auth_endpoint = os.environ.get("ALPHASENSE_AUTH_ENDPOINT")
            if not self.auth_endpoint:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_AUTH_ENDPOINT'} or 'auth_endpoint' config not found."
                )

    def _set_graphql_schema_endpoint(self):
        if not self.graphql_schema_endpoint:
            self.graphql_schema_endpoint = os.environ.get(
                "ALPHASENSE_GRAPHQL_SCHEMA_ENDPOINT"
            )
            if not self.graphql_schema_endpoint:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_GRAPHQL_SCHEMA_ENDPOINT'} or 'graphql_schema_endpoint' config not found."
                )

    def _set_api_endpoint(self):
        if not self.api_endpoint:
            self.api_endpoint = os.environ.get("ALPHASENSE_API_ENDPOINT")
            if not self.api_endpoint:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_API_ENDPOINT'} or 'api_endpoint' config not found."
                )


@dataclass
class AuthConfig(BaseConfig):
    username: str = ""
    password: str = ""
    api_key: str = ""
    client_id: str = ""
    client_secret: str = ""

    def __post_init__(self):
        self._set_username()
        self._set_password()
        self._set_api_key()
        self._set_client_id()
        self._set_client_secret()

        return super().__post_init__()

    def _set_username(self):
        if not self.username:
            self.username = os.environ.get("ALPHASENSE_USERNAME")
            if not self.username:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_USERNAME'} or 'username' config not found."
                )

    def _set_password(self):
        if not self.password:
            self.password = os.environ.get("ALPHASENSE_PASSWORD")
            if not self.password:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_PASSWORD'} or 'password' config not found."
                )

    def _set_api_key(self):
        if not self.api_key:
            self.api_key = os.environ.get("ALPHASENSE_API_KEY")
            if not self.api_key:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_API_KEY'} or 'api_key' config not found."
                )

    def _set_client_id(self):
        if not self.client_id:
            self.client_id = os.environ.get("ALPHASENSE_CLIENT_ID")
            if not self.client_id:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_CLIENT_ID'} or 'client_id' config not found."
                )

    def _set_client_secret(self):
        if not self.client_secret:
            self.client_secret = os.environ.get("ALPHASENSE_CLIENT_SECRET")
            if not self.client_secret:
                raise InvalidConfiguration(
                    f"Environment variable {'ALPHASENSE_CLIENT_SECRET'} or 'client_secret' config not found."
                )


def get_config_section(config_dict: Dict, section_name: str = "schema") -> Dict:
    """Get section from config dict."""
    as_key = ALPHASENSE_KEY
    if as_key in config_dict and section_name in config_dict.get(as_key, {}):
        return config_dict[as_key][section_name]

    if section_name in config_dict:
        warn(
            f"Support for [{section_name}] section has been deprecated "
            "and will be dropped in future release. "
            f"Instead use [{as_key}.{section_name}].",
            DeprecationWarning,
            stacklevel=2,
        )
        return config_dict[section_name]

    raise MissingConfiguration(f"Config has no [{as_key}.{section_name}] section.")


def get_config_file_path(file_name: str = "pyproject.toml") -> Path:
    """Get config file path. If not found raise exception."""
    directory = Path.cwd()
    while not directory.joinpath(file_name).exists():
        if directory == directory.parent:
            raise ConfigFileNotFound(f"Config file {file_name} not found.")
        directory = directory.parent
    return directory.joinpath(file_name).resolve()


def get_config(config_file_name: Optional[str] = None) -> AuthConfig:
    """Get config dict."""
    if config_file_name:
        config_file_path = get_config_file_path(config_file_name)
    else:
        config_file_path = get_config_file_path()

    loaded_cfg = toml.load(config_file_path)
    auth_cfg = get_config_section(loaded_cfg, "auth")

    settings_fields_names = {f.name for f in fields(AuthConfig)}

    return AuthConfig(
        **{
            key: value
            for key, value in auth_cfg.items()
            if key in settings_fields_names
        }
    )
