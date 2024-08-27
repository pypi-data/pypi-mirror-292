from dataclasses import fields
from pathlib import Path
from typing import Dict, Optional
from warnings import simplefilter, warn

import toml
import json

from .client_generators.scalars import ScalarData
from .exceptions import ConfigFileNotFound, MissingConfiguration
from .settings import (
    ClientSettings,
    CommentsStrategy,
    GraphQLSchemaSettings,
    AuthSettings,
)
from .constants import (
    ALPHASENSE_KEY,
)

simplefilter("default", DeprecationWarning)


def get_config_file_path(file_name: str = "pyproject.toml") -> Path:
    """Get config file path. If not found raise exception."""
    directory = Path.cwd()
    while not directory.joinpath(file_name).exists():
        if directory == directory.parent:
            raise ConfigFileNotFound(f"Config file {file_name} not found.")
        directory = directory.parent
    return directory.joinpath(file_name).resolve()


def get_config_dict(config_file_name: Optional[str] = None) -> Dict:
    """Get config dict."""
    if config_file_name:
        config_file_path = get_config_file_path(config_file_name)
    else:
        config_file_path = get_config_file_path()

    return toml.load(config_file_path)


def get_client_settings(config_dict: Dict) -> ClientSettings:
    """Parse configuration dict and return ClientSettings instance."""
    section = get_config_section(config_dict).copy()
    settings_fields_names = {f.name for f in fields(ClientSettings)}
    try:
        section["scalars"] = {
            name: ScalarData(
                type_=data["type"],
                serialize=data.get("serialize"),
                parse=data.get("parse"),
                import_=data.get("import"),
            )
            for name, data in section.get("scalars", {}).items()
        }
    except KeyError as exc:
        raise MissingConfiguration(
            "Missing 'type' field for scalar definition"
        ) from exc

    try:
        if "include_comments" in section and isinstance(
            section["include_comments"], bool
        ):
            section["include_comments"] = (
                CommentsStrategy.TIMESTAMP.value
                if section["include_comments"]
                else CommentsStrategy.NONE.value
            )
            options = ", ".join(strategy.value for strategy in CommentsStrategy)
            warn(
                "Support for boolean 'include_comments' value has been deprecated "
                "and will be dropped in future release. "
                f"Instead use one of following options: {options}",
                DeprecationWarning,
                stacklevel=2,
            )

        return ClientSettings(
            **{
                key: value
                for key, value in section.items()
                if key in settings_fields_names
            }
        )
    except TypeError as exc:
        missing_fields = settings_fields_names.difference(section)
        raise MissingConfiguration(
            f"Missing configuration fields: {', '.join(missing_fields)}"
        ) from exc


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


def get_graphql_schema_settings(config_dict: Dict) -> GraphQLSchemaSettings:
    """Parse configuration dict and return GraphQLSchemaSettings instance."""
    section = get_config_section(config_dict)
    settings_fields_names = {f.name for f in fields(GraphQLSchemaSettings)}
    try:
        return GraphQLSchemaSettings(
            **{
                key: value
                for key, value in section.items()
                if key in settings_fields_names
            }
        )
    except TypeError as exc:
        missing_fields = settings_fields_names.difference(section)
        raise MissingConfiguration(
            f"Missing configuration fields: {', '.join(missing_fields)}"
        ) from exc


def get_auth_settings(config_dict: Dict) -> AuthSettings:
    """Parse configuration dict and return AsAuthSettings instance."""
    auth_cfg = get_config_section(config_dict, "auth").copy()
    cfg = get_config_section(config_dict)

    auth_cfg["schema_path"] = cfg.get("schema_path")
    if auth_cfg.get("schema_path") is None:
        auth_cfg["remote_schema_url"] = cfg.get("remote_schema_url")
    settings_fields_names = {f.name for f in fields(AuthSettings)}
    try:
        return AuthSettings(
            **{
                key: value
                for key, value in auth_cfg.items()
                if key in settings_fields_names
            }
        )
    except TypeError as exc:
        missing_fields = settings_fields_names.difference(auth_cfg)
        raise MissingConfiguration(
            f"Missing configuration fields: {', '.join(missing_fields)}"
        ) from exc
