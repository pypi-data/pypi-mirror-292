from exponent.core.remote_execution import files
from exponent.core.remote_execution.types import (
    CommandRequest,
    CommandResponse,
)
from exponent.core.types.generated.command_request_data import (
    FileReadCommandRequestData,
)


async def execute_command(
    request: CommandRequest,
) -> CommandResponse:
    try:
        match request:
            case CommandRequest(
                correlation_id=correlation_id,
                data=FileReadCommandRequestData(file_path=file_path),
            ):
                return CommandResponse(
                    content=files.read_file(file_path),
                    correlation_id=correlation_id,
                )
            case _:
                raise ValueError(f"Unknown command request: {request}")
    except Exception as e:  # noqa: BLE001 - TODO (Josh): Specialize errors for execution
        return CommandResponse(
            content="An error occurred during command execution: " + str(e),
            correlation_id=request.correlation_id,
        )
