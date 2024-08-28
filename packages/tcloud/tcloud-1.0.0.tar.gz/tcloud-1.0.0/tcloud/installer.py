from __future__ import annotations

import typing as t
import logging

import requests
import os
from importlib.metadata import version, PackageNotFoundError
from urllib.parse import urlencode, urljoin

from tcloud.config import TCloudProject
from tcloud import pip_helper as pip

logger = logging.getLogger(__name__)

PACKAGE_NAME = "sqlmesh-enterprise"


def install_sqlmesh_enterprise(project: TCloudProject, previous_extras: t.List[str]) -> bool:
    """Downloads and installs / upgrades the SQLMesh Enterprise package if needed.

    Args:
        project: The target project.
        previous_extras: The extras that were previously installed.

    Returns:
        True if the package was installed or upgraded, False otherwise.
    """
    _configure_state_connection(project)

    # Use the package metadata to avoid importing the package.
    try:
        current_version = version(PACKAGE_NAME)
    except PackageNotFoundError:
        current_version = None

    upgrade_info = _get_enterprise_version_upgrade(project, current_version)
    target_version = upgrade_info["target_version"]
    # Check `upgrade_info` for extras in case the API supports this in the future
    extras = set((project.extras or []) + upgrade_info.get("extras", []))  # type: ignore

    if current_version == target_version and extras.issubset(previous_extras):
        return False

    pip.install(
        PACKAGE_NAME,
        version=target_version,  # type: ignore
        extra_index_url=upgrade_info.get("extra_index_url"),  # type: ignore
        upgrade=True,
        extras=list(extras),
    )

    return True


def _get_enterprise_version_upgrade(
    project: TCloudProject, current_version: t.Optional[str]
) -> t.Dict[str, t.Union[str, t.List[str]]]:
    url = project.url
    if not url.endswith("/"):
        url += "/"

    upgrade_url = urljoin(url, "state_sync/enterprise_version/upgrade")
    if current_version:
        url_params = urlencode({"current_version": current_version})
        upgrade_url += f"?{url_params}"

    response = requests.get(upgrade_url, headers={"Authorization": f"Bearer {project.token}"})
    response.raise_for_status()
    return response.json()


def _configure_state_connection(project: TCloudProject) -> None:
    state_connection_env_prefix = f"SQLMESH__GATEWAYS__{project.gateway.upper()}__STATE_CONNECTION"
    os.environ[f"{state_connection_env_prefix}__TYPE"] = "cloud"
    os.environ[f"{state_connection_env_prefix}__URL"] = project.url
    os.environ[f"{state_connection_env_prefix}__TOKEN"] = project.token
    os.environ["SQLMESH__DEFAULT_GATEWAY"] = project.gateway
