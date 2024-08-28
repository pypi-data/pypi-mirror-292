from __future__ import annotations

import requests
import typing as t

import click

from tcloud.config import load_project_config, load_previous_extras, save_previous_extras
from tcloud.installer import install_sqlmesh_enterprise


def _tcloud_version() -> str:
    try:
        from tcloud import __version__

        return __version__
    except ImportError:
        return "0.0.0"


class DynamicGroup(click.Group):
    COMMANDS = ["sqlmesh", "sqlmesh_cicd"]

    def list_commands(self, ctx: click.Context) -> t.List[str]:
        return super().list_commands(ctx) + self.COMMANDS

    def get_command(self, ctx: click.Context, cmd_name: str) -> t.Optional[click.Command]:
        if cmd_name in self.COMMANDS:
            return self._load_sqlmesh_enterprise(cmd_name, ctx.params.get("project"))
        return super().get_command(ctx, cmd_name)

    def _load_sqlmesh_enterprise(self, cmd_name: str, project: t.Optional[str]) -> click.Command:
        try:
            project_config = load_project_config(project)
            installed = install_sqlmesh_enterprise(
                project_config, load_previous_extras(project_config.url)
            )
            if installed:
                save_previous_extras(project_config.url, project_config.extras or [])
        except (ValueError, requests.exceptions.RequestException) as ex:
            raise click.ClickException(str(ex)) from ex

        if cmd_name == "sqlmesh_cicd":
            from sqlmesh_enterprise.cli.bot import bot

            return bot

        from sqlmesh_enterprise.cli.main import cli

        return cli


@click.group(cls=DynamicGroup, no_args_is_help=True)
@click.version_option(version=_tcloud_version(), message="%(version)s")
@click.option(
    "--project",
    type=str,
    help="The name of the project.",
)
def cli(project: t.Optional[str]) -> None:
    pass
