import json

import click
from exponent.commands.common import (
    redirect_to_login,
    run_until_complete,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import exponent_cli_group
from exponent.core.config import Settings
from exponent.core.graphql.client import GraphQLClient
from exponent.core.graphql.get_chats_query import GET_CHATS_QUERY
from exponent.core.graphql.subscriptions import AUTHENTICATED_USER_SUBSCRIPTION


@exponent_cli_group()
def config_cli() -> None:
    pass


@config_cli.command()
@use_settings
def config(settings: Settings) -> None:
    config_file_settings = settings.get_config_file_settings()

    click.secho(
        json.dumps(config_file_settings, indent=2),
        fg="green",
    )


@config_cli.command()
@click.option("--key", help="Your Exponent API Key")
@use_settings
def login(settings: Settings, key: str) -> None:
    if not key:
        redirect_to_login(settings, "provided")
        return

    click.echo(f"Saving API Key to {settings.config_file_path}")

    if settings.api_key and settings.api_key != key:
        click.confirm("Detected existing API Key, continue? ", default=True, abort=True)

    settings.update_api_key(key)
    settings.write_settings_to_config_file()

    click.echo("API Key saved.")


@config_cli.command()
@use_settings
def get_chats(
    settings: Settings,
) -> None:
    if not settings.api_key:
        redirect_to_login(settings)
        return

    run_until_complete(
        get_chats_task(
            api_key=settings.api_key,
            base_api_url=settings.base_api_url,
        )
    )


@config_cli.command()
@use_settings
def get_authenticated_user(
    settings: Settings,
) -> None:
    if not settings.api_key:
        redirect_to_login(settings)
        return

    run_until_complete(
        get_authenticated_user_task(
            api_key=settings.api_key,
            base_api_url=settings.base_api_url,
        )
    )


async def get_chats_task(
    api_key: str,
    base_api_url: str,
) -> None:
    graphql_client = GraphQLClient(api_key, base_api_url)
    result = await graphql_client.query(GET_CHATS_QUERY)
    click.echo(result)


async def get_authenticated_user_task(
    api_key: str,
    base_api_url: str,
) -> None:
    graphql_client = GraphQLClient(api_key, base_api_url)
    async for it in graphql_client.subscribe(AUTHENTICATED_USER_SUBSCRIPTION):
        click.echo(it)
