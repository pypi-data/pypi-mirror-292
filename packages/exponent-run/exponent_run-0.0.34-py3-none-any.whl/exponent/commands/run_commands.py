import click
from exponent.commands.common import (
    create_chat,
    redirect_to_login,
    run_until_complete,
    start_client,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import exponent_cli_group
from exponent.commands.utils import launch_exponent_browser, print_exponent_message
from exponent.core.config import Environment, Settings


@exponent_cli_group()
def run_cli() -> None:
    pass


@run_cli.command()
@click.option(
    "--chat-id",
    help="ID of an existing chat session to reconnect",
    required=False,
)
@click.option(
    "--prompt",
    help="Start a chat with a given prompt.",
)
@click.option(
    "--benchmark",
    is_flag=True,
    help="Enable benchmarking mode",
)
@use_settings
def run(
    settings: Settings,
    chat_id: str | None = None,
    prompt: str | None = None,
    benchmark: bool = False,
) -> None:
    if not settings.api_key:
        redirect_to_login(settings)
        return

    run_until_complete(
        start_run(
            settings.environment,
            settings.api_key,
            settings.base_url,
            settings.base_api_url,
            chat_uuid=chat_id,
            prompt=prompt,
            benchmark=benchmark,
        )
    )


async def start_run(  # noqa: PLR0913
    environment: Environment,
    api_key: str,
    base_url: str,
    base_api_url: str,
    chat_uuid: str | None = None,
    prompt: str | None = None,
    benchmark: bool = False,
) -> None:
    if chat_uuid is None:
        chat_uuid = await create_chat(api_key, base_api_url)

        if chat_uuid is None:
            return

        if not benchmark and not prompt:
            # Open the chat in the browser
            launch_exponent_browser(environment, base_url, chat_uuid)

    print_exponent_message(base_url, chat_uuid)

    await start_client(
        api_key,
        base_api_url,
        chat_uuid,
        prompt,
        benchmark,
    )
