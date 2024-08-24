import click

from exponent.commands.cloud_commands import (
    cloud_cli,
)
from exponent.commands.common import (
    set_log_level,
)
from exponent.commands.config_commands import config_cli
from exponent.commands.run_commands import run_cli
from exponent.commands.shell_commands import shell_cli
from exponent.commands.types import ExponentGroup, exponent_cli_group
from exponent.commands.utils import check_exponent_version
from exponent.core.config import is_editable_install
from exponent.version import get_version


@exponent_cli_group()
@click.version_option(get_version(), prog_name="Exponent CLI")
def cli() -> None:
    """Exponent CLI group."""
    set_log_level()
    if not is_editable_install():
        check_exponent_version()


sources: list[ExponentGroup] = [config_cli, run_cli, shell_cli, cloud_cli]

for source in sources:
    for command in source.commands.values():
        cli.add_command(command)

if __name__ == "__main__":
    cli()
