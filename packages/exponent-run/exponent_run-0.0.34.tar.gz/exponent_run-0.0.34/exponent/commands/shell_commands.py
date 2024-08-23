import asyncio
import shutil
import sys
import time
from collections.abc import Callable, Coroutine, Iterable
from concurrent.futures import Future
from typing import Any

import click
from exponent.commands.common import (
    create_chat,
    inside_ssh_session,
    redirect_to_login,
    start_client,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import (
    StrategyChoice,
    StrategyOption,
    exponent_cli_group,
)
from exponent.commands.utils import start_background_event_loop
from exponent.core.config import Settings
from exponent.core.graphql.client import GraphQLClient
from exponent.core.graphql.mutations import HALT_CHAT_STREAM_MUTATION
from exponent.core.graphql.subscriptions import CHAT_EVENTS_SUBSCRIPTION
from exponent.core.remote_execution.exceptions import ExponentError
from exponent.core.types.generated.strategy_info import (
    ENABLED_STRATEGY_INFO_LIST,
)
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.syntax import Syntax

SLASH_COMMANDS = {
    "/help": "Show available commands",
    "/autorun": "Toggle autorun mode",
    "/web": "Move chat to a web browser",
}


@exponent_cli_group()
def shell_cli() -> None:
    pass


@shell_cli.command()
@click.option(
    "--model",
    help="LLM model",
    required=True,
    default="CLAUDE_3_POINT_5_SONNET",
)
@click.option(
    "--strategy",
    prompt=True,
    prompt_required=False,
    type=StrategyChoice(ENABLED_STRATEGY_INFO_LIST),
    cls=StrategyOption,
)
@click.option(
    "--autorun",
    is_flag=True,
    help="Enable autorun mode",
)
@click.option(
    "--prompt",
    help="Initial prompt",
)
@use_settings
def shell(
    settings: Settings,
    model: str,
    strategy: str,
    autorun: bool = False,
    prompt: str | None = None,
) -> None:
    if not settings.api_key:
        redirect_to_login(settings)
        return

    api_key = settings.api_key
    base_api_url = settings.base_api_url
    gql_client = GraphQLClient(api_key, base_api_url)
    loop = start_background_event_loop()

    chat_uuid = asyncio.run_coroutine_threadsafe(
        create_chat(api_key, base_api_url), loop
    ).result()

    if chat_uuid is None:
        sys.exit(1)

    client_fut = asyncio.run_coroutine_threadsafe(
        start_client(api_key, base_api_url, chat_uuid), loop
    )

    input_handler = InputHandler()
    chat = Chat(chat_uuid, settings.base_url, gql_client, model, strategy, autorun)
    shell = Shell(prompt, loop, input_handler, chat)
    shell.run()
    client_fut.cancel()
    print("\rBye!")


def pause_spinner(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(self: "Chat", *args: Any, **kwargs: Any) -> Any:
        self.spinner.hide()
        result = func(self, *args, **kwargs)
        self.spinner.show()
        return result

    return wrapper


def stop_spinner(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(self: "Chat", *args: Any, **kwargs: Any) -> Any:
        self.spinner.hide()
        result = func(self, *args, **kwargs)
        return result

    return wrapper


class Chat:
    def __init__(  # noqa: PLR0913
        self,
        chat_uuid: str,
        base_url: str,
        gql_client: GraphQLClient,
        model: str,
        strategy: str,
        autorun: bool,
    ) -> None:
        self.chat_uuid = chat_uuid
        self.base_url = base_url
        self.gql_client = gql_client
        self.model = model
        self.strategy = strategy
        self.autorun = autorun
        self.parent_uuid: str | None = None
        self.block_row_offset = 0
        self.console = Console()
        self.code_block_uuid = None
        self.file_write_uuid = None
        self.command_uuid = None
        self.block: Block = NullBlock()
        self.spinner = Spinner("Exponent is working...")

    async def send_prompt(self, prompt: str) -> str | None:
        self.spinner.show()

        return await self.process_chat_subscription(
            {"prompt": {"message": prompt, "attachments": []}}
        )

    async def send_confirmation(self) -> str | None:
        if self.code_block_uuid is not None:
            return await self.process_chat_subscription(
                {
                    "codeBlockConfirmation": {
                        "accepted": True,
                        "codeBlockUuid": self.code_block_uuid,
                    }
                }
            )
        elif self.file_write_uuid is not None:
            return await self.process_chat_subscription(
                {
                    "fileWriteConfirmation": {
                        "accepted": True,
                        "fileWriteUuid": self.file_write_uuid,
                    }
                }
            )
        elif self.command_uuid is not None:
            return await self.process_chat_subscription(
                {
                    "commandConfirmation": {
                        "accepted": True,
                        "commandUuid": self.command_uuid,
                    }
                }
            )

        return None

    def toggle_autorun(self) -> bool:
        self.autorun = not self.autorun
        return self.autorun

    async def halt_stream(self) -> None:
        await self.gql_client.query(
            HALT_CHAT_STREAM_MUTATION, {"chatUuid": self.chat_uuid}, "HaltChatStream"
        )

    def url(self) -> str:
        return f"{self.base_url}/chats/{self.chat_uuid}"

    async def process_chat_subscription(  # noqa: PLR0912, PLR0915
        self,
        extra_vars: dict[str, Any],
    ) -> str | None:
        result = None

        vars = {
            "chatUuid": self.chat_uuid,
            "parentUuid": self.parent_uuid,
            "model": self.model,
            "strategyNameOverride": self.strategy,
            "useToolsConfig": "read_write",
            "requireConfirmation": not self.autorun,
        }

        vars.update(extra_vars)
        self.code_block_uuid = None
        self.file_write_uuid = None
        self.command_uuid = None

        async for response in self.gql_client.subscribe(CHAT_EVENTS_SUBSCRIPTION, vars):
            event = response["authenticatedChat"]
            kind = event["__typename"]

            self.parent_uuid = event.get("eventUuid") or self.parent_uuid

            if kind == "MessageChunkEvent":
                if event["role"] == "assistant":
                    self.handle_message_chunk_event(event)
            elif kind == "MessageEvent":
                if event["role"] == "assistant":
                    self.handle_message_event(event)
            elif kind == "FileWriteChunkEvent":
                self.handle_file_write_chunk_event(event)
            elif kind == "FileWriteEvent":
                self.handle_file_write_event(event)
            elif kind == "FileWriteConfirmationEvent":
                self.handle_file_write_confirmation_event(event)
            elif kind == "FileWriteStartEvent":
                self.handle_file_write_start_event(event)
            elif kind == "FileWriteResultEvent":
                self.handle_file_write_result_event(event)
            elif kind == "CodeBlockChunkEvent":
                self.handle_code_block_chunk_event(event)
            elif kind == "CodeBlockEvent":
                self.handle_code_block_event(event)
            elif kind == "CodeBlockConfirmationEvent":
                self.handle_code_block_confirmation_event(event)
            elif kind == "CodeExecutionStartEvent":
                self.handle_code_execution_start_event(event)
            elif kind == "CodeExecutionEvent":
                self.handle_code_execution_event(event)
            elif kind == "CommandChunkEvent":
                if event["data"]["type"] == "THINKING":
                    continue
                self.handle_command_chunk_event(event)
            elif kind == "CommandEvent":
                if event["data"]["type"] == "THINKING":
                    continue
                self.handle_command_event(event)
            elif kind == "CommandConfirmationEvent":
                self.handle_command_confirmation_event(event)
            elif kind == "CommandStartEvent":
                self.handle_command_start_event(event)
            elif kind == "CommandResultEvent":
                self.handle_command_result_event(event)
            elif kind == "Error":
                raise ExponentError(event["message"])
            else:
                # TODO
                pass

        self.spinner.hide()
        return result

    @stop_spinner
    def handle_message_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.block.event_uuid != event_uuid:
            seqs.append(self.block.end())
            self.block = MessageBlock(event_uuid)

        assert isinstance(self.block, MessageBlock)
        seqs.append(self.block.update(content=event["content"]))
        render(seqs)

    @pause_spinner
    def handle_message_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.block.event_uuid != event_uuid:
            seqs.append(self.block.end())
            self.block = MessageBlock(event_uuid)

        assert isinstance(self.block, MessageBlock)
        seqs.append(self.block.update(status="done", content=event["content"]))
        render(seqs)

    @stop_spinner
    def handle_file_write_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.block.event_uuid != event_uuid:
            seqs.append(self.block.end())
            self.block = FileWriteBlock(
                event_uuid, event["language"], event["filePath"]
            )
            seqs.append(self.block.start())

        assert isinstance(self.block, FileWriteBlock)
        seqs.append(self.block.update(content=event["content"]))
        render(seqs)

    @pause_spinner
    def handle_file_write_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.block.event_uuid != event_uuid:
            seqs.append(self.block.end())
            self.block = FileWriteBlock(
                event_uuid, event["language"], event["filePath"]
            )
            seqs.append(self.block.start())

        assert isinstance(self.block, FileWriteBlock)
        seqs.append(self.block.update(content=event["content"]))

        if event["requireConfirmation"]:
            seqs.append(self.block.update(status="requires_confirmation"))
            self.file_write_uuid = event_uuid
        else:
            seqs.append(self.block.update(status="executing"))

        render(seqs)

    @pause_spinner
    def handle_file_write_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.block.event_uuid == event["fileWriteUuid"]:
            assert isinstance(self.block, FileWriteBlock)
            seqs = []

            if event["accepted"]:
                seqs.append(self.block.update(status="executing"))
            else:
                # user entered new prompt, cursor moved 2 lines down
                # therefore we need to move it back where it was
                seqs.append([move_cursor_up_seq(2), erase_display_seq()])
                seqs.append(self.block.update(status="rejected"))

            render(seqs)

    @pause_spinner
    def handle_file_write_start_event(self, event: dict[str, Any]) -> None:
        if self.block.event_uuid == event["fileWriteUuid"]:
            assert isinstance(self.block, FileWriteBlock)
            render(self.block.update(status="executing"))

    @pause_spinner
    def handle_file_write_result_event(self, event: dict[str, Any]) -> None:
        if self.block.event_uuid == event["fileWriteUuid"]:
            assert isinstance(self.block, FileWriteBlock)
            render(self.block.update(status="done", result=event["content"]))

    @stop_spinner
    def handle_command_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.block.event_uuid != event_uuid:
            seqs.append(self.block.end())
            self.block = CommandBlock(event_uuid, str(event["data"]["type"]).lower())
            seqs.append(self.block.start())

        assert isinstance(self.block, CommandBlock)
        seqs.append(self.block.update(data=event["data"]))
        render(seqs)

    @pause_spinner
    def handle_command_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.block.event_uuid != event_uuid:
            seqs.append(self.block.end())
            self.block = CommandBlock(event_uuid, str(event["data"]["type"]).lower())
            seqs.append(self.block.start())

        assert isinstance(self.block, CommandBlock)
        seqs.append(self.block.update(data=event["data"]))

        if event["requireConfirmation"]:
            seqs.append(self.block.update(status="requires_confirmation"))
            self.command_uuid = event_uuid
        else:
            seqs.append(self.block.update(status="executing"))

        render(seqs)

    @pause_spinner
    def handle_command_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.block.event_uuid == event["commandUuid"]:
            assert isinstance(self.block, CommandBlock)
            seqs = []

            if event["accepted"]:
                seqs.append(self.block.update(status="executing"))
            else:
                # user entered new prompt, cursor moved 2 lines down
                # therefore we need to move it back where it was
                seqs.append([move_cursor_up_seq(2), erase_display_seq()])
                seqs.append(self.block.update(status="rejected"))

            render(seqs)

    @pause_spinner
    def handle_command_start_event(self, event: dict[str, Any]) -> None:
        if self.block.event_uuid == event["commandUuid"]:
            assert isinstance(self.block, CommandBlock)
            render(self.block.update(status="executing"))

    @pause_spinner
    def handle_command_result_event(self, event: dict[str, Any]) -> None:
        if self.block.event_uuid == event["commandUuid"]:
            assert isinstance(self.block, CommandBlock)
            render(self.block.update(status="done", result=event["content"]))

    @stop_spinner
    def handle_code_block_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.block.event_uuid != event_uuid:
            seqs.append(self.block.end())
            self.block = CodeBlock(event_uuid, event["language"], event["language"])
            seqs.append(self.block.start())

        assert isinstance(self.block, CodeBlock)
        seqs.append(self.block.update(content=event["content"]))
        render(seqs)

    @pause_spinner
    def handle_code_block_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.block.event_uuid != event_uuid:
            seqs.append(self.block.end())
            self.block = CodeBlock(event_uuid, event["language"], event["language"])
            seqs.append(self.block.start())

        assert isinstance(self.block, CodeBlock)
        seqs.append(self.block.update(content=event["content"]))

        if event["requireConfirmation"]:
            seqs.append(self.block.update(status="requires_confirmation"))
            self.code_block_uuid = event_uuid
        else:
            seqs.append(self.block.update(status="executing"))

        render(seqs)

    @pause_spinner
    def handle_code_block_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.block.event_uuid == event["codeBlockUuid"]:
            assert isinstance(self.block, CodeBlock)
            seqs = []

            if event["accepted"]:
                seqs.append(self.block.update(status="executing"))
            else:
                # user entered new prompt, cursor moved 2 lines down
                # therefore we need to move it back where it was
                seqs.append([move_cursor_up_seq(2), erase_display_seq()])
                seqs.append(self.block.update(status="rejected"))

            render(seqs)

    @pause_spinner
    def handle_code_execution_start_event(self, event: dict[str, Any]) -> None:
        if self.block.event_uuid == event["codeBlockUuid"]:
            assert isinstance(self.block, CodeBlock)
            render(self.block.update(status="executing"))

    @pause_spinner
    def handle_code_execution_event(self, event: dict[str, Any]) -> None:
        seqs = []
        output = OutputBlock(event["eventUuid"], event["content"])

        if self.block.event_uuid == event["codeBlockUuid"]:
            assert isinstance(self.block, CodeBlock)
            seqs.append(self.block.update(status="done", output=output))
        else:
            # If the code block UUID doesn't match, create a standalone OutputBlock
            seqs.append(self.block.end())
            self.block = output
            seqs.append(self.block.start())

        render(seqs)


class Spinner:
    def __init__(self, text: str) -> None:
        self.text = text
        self.task: asyncio.Task[None] | None = None
        self.base_time = time.time()

    def show(self) -> None:
        if self.task is not None:
            return

        async def spinner(base_time: float) -> None:
            chars = "⣷⣯⣟⡿⢿⣻⣽⣾"

            while True:
                t = time.time() - base_time
                i = round(t * 10) % len(chars)
                render(["\r", chars[i], f" {self.text}"])
                await asyncio.sleep(0.1)

        self.task = asyncio.get_event_loop().create_task(spinner(self.base_time))

    def hide(self) -> None:
        if self.task is None:
            return

        self.task.cancel()
        self.task = None
        render([clear_line_seq()])


class InputHandler:
    def __init__(self) -> None:
        self.kb = KeyBindings()
        self.shortcut_pressed = None
        self.session: PromptSession[Any] = PromptSession(
            completer=SlashCommandCompleter(),
            complete_while_typing=False,
            key_bindings=self.kb,
        )

        @self.kb.add("c-y")
        def _(event: Any) -> None:
            self.shortcut_pressed = "<c-y>"
            event.app.exit()

        @self.kb.add("c-d")
        def _(event: Any) -> None:
            self.shortcut_pressed = "<c-d>"
            event.app.exit()

    def prompt(self) -> str:
        self.shortcut_pressed = None
        user_input = self.session.prompt(HTML("<b><ansigreen>></ansigreen></b> "))

        if self.shortcut_pressed:
            return self.shortcut_pressed
        else:
            assert isinstance(user_input, str)
            return user_input


class Shell:
    def __init__(
        self,
        prompt: str | None,
        loop: asyncio.AbstractEventLoop,
        input_handler: InputHandler,
        chat: Chat,
    ) -> None:
        self.prompt = prompt
        self.loop = loop
        self.input_handler = input_handler
        self.chat = chat
        self.stream_fut: Future[Any] | None = None

    def run(self) -> None:
        self._print_welcome_message()
        self._send_initial_prompt()

        while True:
            try:
                self._wait_for_stream_completion()
                text = self.input_handler.prompt()

                if text.startswith("/"):
                    self._run_command(text[1:].strip())
                elif text == "<c-y>":
                    self._confirm_execution()
                elif text in {"q", "exit"}:
                    print()
                    break
                elif text == "<c-d>":
                    print()
                    do_quit = self._ask_for_quit_confirmation()
                    print()

                    if do_quit:
                        break
                elif text:
                    print()
                    self._send_prompt(text)

            except KeyboardInterrupt:
                if self.stream_fut is not None:
                    self._run_coroutine(self.chat.halt_stream()).result()
                else:
                    do_quit = self._ask_for_quit_confirmation()
                    print()

                    if do_quit:
                        break

            except ExponentError as e:
                self._print_error_message(e)
                break

    def _print_welcome_message(self) -> None:
        print("Welcome to ✨ \x1b[1;32mExponent \x1b[4:3mSHELL\x1b[0m ✨")
        print()
        print("Type 'q', 'exit' or press <C-c> to exit")
        print("Enter '/help' to see a list of available commands")
        print()

    def _print_error_message(self, e: ExponentError) -> None:
        print(f"\n\n\x1b[1;31m{e}\x1b[0m")
        print("\x1b[3;33m")
        print("Please try again and reach out if the problem persists.")
        print("\x1b[0m")

    def _show_help(self) -> None:
        print()

        for command, description in SLASH_COMMANDS.items():
            print(f"{command} - {description}")

        print()

    def _run_command(self, command: str) -> None:
        if command == "help":
            self._show_help()
        elif command == "autorun":
            self._toggle_autorun()
        elif command == "web":
            self._switch_chat_to_web()
        else:
            print(f"\nUnknown command: {command}\n")

    def _ask_for_quit_confirmation(self) -> bool:
        while True:
            answer = input("Do you want to quit Exponent shell? [y/N] ").strip().lower()

            if answer in {"y", "yes"}:
                return True
            elif answer in {"n", "no", ""}:
                return False

    def _toggle_autorun(self) -> None:
        if self.chat.toggle_autorun():
            print("\nAutorun mode enabled\n")
        else:
            print("\nAutorun mode disabled\n")

    def _switch_chat_to_web(self) -> None:
        url = self.chat.url()
        print(f"\nThis chat has been moved to {url}\n")

        if not inside_ssh_session():
            click.launch(url)

        while True:
            input()

    def _confirm_execution(self) -> None:
        render(
            [
                "\r",
                move_cursor_up_seq(1),
                clear_line_seq(),
            ]
        )

        self.stream_fut = self._run_coroutine(self.chat.send_confirmation())

    def _send_initial_prompt(self) -> None:
        if self.prompt is not None:
            self._send_prompt(self.prompt)

    def _send_prompt(self, text: str) -> None:
        self.stream_fut = self._run_coroutine(self.chat.send_prompt(text))

    def _wait_for_stream_completion(self) -> None:
        if self.stream_fut is not None:
            self.stream_fut.result()
            self.stream_fut = None

    def _run_coroutine(self, coro: Coroutine[Any, Any, Any]) -> Future[Any]:
        return asyncio.run_coroutine_threadsafe(coro, self.loop)


class SlashCommandCompleter(Completer):
    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text = document.text
        if text.startswith("/"):
            for command in SLASH_COMMANDS:
                if command.startswith(text):
                    yield Completion(command, start_position=-len(text))


class Block:
    def __init__(self, event_uuid: str) -> None:
        self.event_uuid = event_uuid
        self.spinner = None
        self.block_row_offset = 0
        self.console = Console()
        self.theme = "monokai"

    def end(self) -> list[Any]:
        return []

    def render_header(self, text: str) -> list[str]:
        return [
            block_header_bg_seq(),
            block_header_fg_seq(),
            erase_line_seq(),
            " " + text,
            reset_attrs_seq(),
            "\n",
        ]

    def render_footer(self, text: str) -> list[str]:
        return [
            block_header_bg_seq(),
            block_header_fg_seq(),
            erase_line_seq(),
            " " + text,
            reset_attrs_seq(),
            "\n",
        ]

    def render_padding(self) -> list[str]:
        return [
            block_body_bg_seq(),
            erase_line_seq(),
            reset_attrs_seq(),
            "\n",
        ]

    def highlight_code(self, code: str, lang: str, line_numbers: bool = True) -> str:
        syntax = Syntax(
            code,
            lang,
            theme=self.theme,
            line_numbers=line_numbers,
            word_wrap=True,
        )

        with self.console.capture() as capture:
            self.console.print(syntax)

        return capture.get()


class NullBlock(Block):
    def __init__(self) -> None:
        super().__init__("")

    def end(self) -> list[Any]:
        return []


class MessageBlock(Block):
    def __init__(self, event_uuid: str) -> None:
        super().__init__(event_uuid)
        self.status = "streaming"
        self.content_len = 0

    def update(
        self, status: str | None = None, content: str | None = None
    ) -> list[Any]:
        self.status = status or self.status

        if content is not None:
            content = content.strip()
            chunk = content[self.content_len :]
            self.content_len = len(content)

            if self.status == "streaming":
                return [chunk]
            else:
                return [chunk, "\n\n"]

        return []


class OutputBlock(Block):
    def __init__(self, event_uuid: str, content: str) -> None:
        super().__init__(event_uuid)
        self.content = content

    def start(self) -> list[Any]:
        return [
            self.render_header("output"),
            self.render_padding(),
            self.render_content(),
        ]

    def end(self) -> list[Any]:
        return [self.render_padding()]

    def render_content(self) -> list[Any]:
        lines = pad_left(self.content.strip(), "  ").split("\n")

        return [[block_body_bg_seq(), erase_line_seq(), line, "\n"] for line in lines]


class CodeBlock(Block):
    def __init__(self, event_uuid: str, lang: str, header_text: str) -> None:
        super().__init__(event_uuid)
        self.status = "streaming"  # valid states: streaming, requires_confirmation, rejected, executing, done
        self.lang = lang
        self.header_text = header_text
        self.output: OutputBlock | None = None
        self.line_count = 0
        self.cursor_row_offset = 0

    def start(self) -> list[Any]:
        return [
            self.render_header(self.header_text),
            self.render_padding(),
        ]

    def update(
        self,
        status: str | None = None,
        content: str | None = None,
        output: OutputBlock | None = None,
    ) -> list[Any]:
        seqs: list[Any] = []

        seqs.append([move_cursor_up_seq(self.cursor_row_offset), clear_line_seq()])
        self.cursor_row_offset = 0

        if self.status == "streaming" and content is not None:
            code = pad_left(content.strip(), "  ")
            code = self.highlight_code(code, self.lang, line_numbers=False)
            lines = code.split("\n")
            lines = lines[0 : len(lines) - 1]
            new_line_count = len(lines)

            if self.line_count > 0:
                seqs.append([move_cursor_up_seq(1), "\r"])
                lines = lines[self.line_count - 1 :]

            lines = [line + "\n" for line in lines]
            seqs.append(lines)
            self.line_count = new_line_count

        if status is not None and status != self.status:
            if self.status == "streaming":
                seqs.append(self.render_padding())

        if output is not None:
            seqs.append(output.start())
            seqs.append(output.end())
            seqs.append(["\n"])
            self.cursor_row_offset = 1

        if status is not None:
            self.status = status
            footer = self.render_status_footer()

            if footer:
                seqs.append([footer, "\n"])
                self.cursor_row_offset = 2

        return seqs

    def render_status_footer(self) -> list[Any]:
        if self.status == "requires_confirmation":
            return self.render_footer(
                "Run this code now with <C+y>. Sending a new message will cancel this request."
            )
        elif self.status == "rejected":
            return self.render_footer("✘ Code did not execute")
        elif self.status == "executing":
            return self.render_footer("⚙️ Running code...")

        return []


class FileWriteBlock(Block):
    def __init__(self, event_uuid: str, lang: str, file_path: str) -> None:
        super().__init__(event_uuid)
        self.status = "streaming"  # valid states: streaming, requires_confirmation, rejected, executing, done
        self.lang = lang
        self.file_path = file_path
        self.result: str | None = None
        self.line_count = 0
        self.cursor_row_offset = 0

    def start(self) -> list[Any]:
        return [
            self.render_header(f"Editing file {self.file_path}"),
            self.render_padding(),
        ]

    def update(
        self,
        status: str | None = None,
        content: str | None = None,
        result: str | None = None,
    ) -> list[Any]:
        seqs: list[Any] = []

        seqs.append([move_cursor_up_seq(self.cursor_row_offset), clear_line_seq()])
        self.cursor_row_offset = 0

        if self.status == "streaming" and content is not None:
            code = pad_left(content.strip(), "  ")
            code = self.highlight_code(code, "rust" or self.lang, line_numbers=False)
            lines = code.split("\n")
            lines = lines[0 : len(lines) - 1]
            new_line_count = len(lines)

            if self.line_count > 0:
                seqs.append([move_cursor_up_seq(1), "\r"])
                lines = lines[self.line_count - 1 :]

            lines = [line + "\n" for line in lines]
            seqs.append(lines)
            self.line_count = new_line_count

        if result is not None:
            self.result = result

        if status is not None:
            if self.status == "streaming":
                seqs.append(self.render_padding())

            self.status = status
            footer = self.render_status_footer()

            if footer:
                seqs.append([footer, "\n"])
                self.cursor_row_offset = 2

        return seqs

    def render_status_footer(self) -> list[Any]:
        if self.status == "requires_confirmation":
            return self.render_footer(
                "Confirm edit with <C+y>. Sending a new message will dismiss code changes."
            )
        elif self.status == "rejected":
            return self.render_footer("✘ Edit dismissed")
        elif self.status == "executing":
            return self.render_footer("⚙️ Applying edit...")
        elif self.status == "done":
            return self.render_footer(
                f"✔️ {self.result}" if self.result else "✔️ Edit applied"
            )

        return []


class CommandBlock(Block):
    def __init__(self, event_uuid: str, type: str) -> None:
        super().__init__(event_uuid)
        self.status = "streaming"  # valid states: streaming, requires_confirmation, rejected, executing, done
        self.type = type
        self.lang: str | None = None
        self.data: dict[str, Any] | None = None
        self.result: str | None = None
        self.line_count = 0
        self.cursor_row_offset = 0

    def start(self) -> list[Any]:
        return [
            self.render_header(self.type),
            self.render_padding(),
        ]

    def update(
        self,
        status: str | None = None,
        data: dict[str, Any] | None = None,
        result: str | None = None,
    ) -> list[Any]:
        if self.type not in ["file_read", "file_open"]:
            return []

        seqs: list[Any] = []

        seqs.append([move_cursor_up_seq(self.cursor_row_offset), clear_line_seq()])
        self.cursor_row_offset = 0

        if self.status == "streaming" and data is not None:
            self.lang = data["language"]
            paths = self.render_paths(data["filePath"])
            new_line_count = len(paths)

            if self.line_count > 0:
                seqs.append([move_cursor_up_seq(1), "\r"])
                paths = paths[self.line_count - 1 :]

            seqs.append(paths)
            self.line_count = new_line_count

        if status is not None and status != self.status:
            if self.status == "streaming":
                seqs.append(self.render_padding())

        if result is not None:
            seqs.append(self.render_output(result))
            self.cursor_row_offset = 1

        if status is not None:
            self.status = status
            footer = self.render_status_footer()

            if footer:
                seqs.append([footer, "\n"])
                self.cursor_row_offset = 2

        return seqs

    def render_paths(self, paths: str) -> list[Any]:
        lines = pad_left(paths.strip(), "  ").split("\n")

        return [[block_body_bg_seq(), erase_line_seq(), line, "\n"] for line in lines]

    def render_output(self, content: str) -> list[Any]:
        header = self.render_header("output")
        padding = self.render_padding()
        code = pad_left(content.strip(), "  ")
        assert self.lang is not None
        code = self.highlight_code(code, self.lang, line_numbers=False)

        return [header, padding, code, padding]

    def render_status_footer(self) -> list[Any]:
        if self.status == "requires_confirmation":
            return self.render_footer(
                f"Confirm {self.type} command with <C+y>. "
                "Sending a new message will cancel this command."
            )
        elif self.status == "rejected":
            return self.render_footer(f"✘ {self.type} command did not execute")
        elif self.status == "executing":
            return self.render_footer(f"⚙️ Executing {self.type} command...")
        elif self.status == "done":
            return self.render_footer(f"✔️ {self.type} command executed")

        return []


def text_line_count(text: str) -> int:
    cols = get_terminal_width()
    count = 0

    for line in text.split("\n"):
        count += len(line) // cols

        if len(line) == 0 or len(line) % cols > 0:
            count += 1

    return count


def get_terminal_width() -> int:
    cols, _ = shutil.get_terminal_size()
    return cols


def pad_left(text: str, padding: str) -> str:
    return "\n".join([padding + line for line in text.strip().split("\n")])


def fg_color_seq(c: int) -> str:
    return f"\x1b[{30 + c}m"


def block_header_bg_seq() -> str:
    return "\x1b[48;2;29;30;24m"


def block_header_fg_seq() -> str:
    return "\x1b[38;5;246m"


def block_body_bg_seq() -> str:
    return "\x1b[48;5;235m"


def erase_line_seq() -> str:
    return "\x1b[2K"


def erase_display_seq() -> str:
    return "\x1b[0J"


def reset_attrs_seq() -> str:
    return "\x1b[0m"


def clear_line_seq() -> str:
    return f"\r{reset_attrs_seq()}{erase_line_seq()}"


def move_cursor_up_seq(n: int) -> str:
    if n > 0:
        return f"\x1b[{n}A"
    else:
        return ""


def render(seqs: str | list[Any] | None) -> int:
    text, newline_count = collect(seqs)
    print(text, end="")
    sys.stdout.flush()

    return newline_count


def collect(seqs: str | list[Any] | None) -> tuple[str, int]:
    if seqs is None:
        return ("", 0)

    if isinstance(seqs, str):
        return (seqs, seqs.count("\n"))

    if isinstance(seqs, tuple):
        return seqs

    assert isinstance(seqs, list)

    text = ""
    newline_count = 0

    for seq in seqs:
        t, c = collect(seq)
        text += t
        newline_count += c

    return (text, newline_count)
