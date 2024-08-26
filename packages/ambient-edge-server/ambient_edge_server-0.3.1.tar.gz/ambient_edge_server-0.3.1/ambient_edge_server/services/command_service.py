import subprocess
from abc import ABC, abstractmethod
from typing import Optional

from ambient_backend_api_client import (
    ApiClient,
    Command,
    CommandNodeRelationship,
    CommandsApi,
    CommandStatusEnum,
    Configuration,
    UpdateNodeRelationship,
)
from result import Err, Ok, Result

from ambient_edge_server.repos.node_repo import NodeRepo
from ambient_edge_server.utils import logger


class CommandService(ABC):
    @abstractmethod
    async def execute(self, command: Command) -> Result[None, str]:
        pass


class CommandServiceLinux(CommandService):
    def __init__(self, node_repo: NodeRepo):
        self.api_config: Configuration | None = None
        self.node_repo = node_repo
        self.node_id = self.node_repo.get_node_id()
        logger.info("CommandServiceLinux initialized")

    async def init(self, api_config: Configuration) -> None:
        self.api_config = api_config
        logger.info("API config saved to CommandServiceLinux")

    async def execute(self, command: Command) -> Result[None, str]:
        logger.info("Executing command: %s", command.command)

        # update status to running
        update_cmd_result = await self.update_command(
            command.id, self.node_id, CommandStatusEnum.RUNNING
        )
        if update_cmd_result.is_err():
            err_msg = f"Failed to update command status to running: \
{update_cmd_result.unwrap_err()}"
            logger.error(err_msg)
            return update_cmd_result
        logger.debug(
            "CommandServiceLinux.execute - updated command status to running: %s",
            update_cmd_result.unwrap().model_dump_json(indent=4),
        )

        # Run the command
        logger.info("Running the command ...")
        result = self.run_command(command)
        if result.is_err():
            err_msg = f"Command failed: {result.unwrap_err()}"
            logger.error(err_msg)
            return result
        logger.info("Command executed successfully.")
        logger.debug(
            "CommandServiceLinux.execute - command result: %s", result.unwrap()
        )

        # update result
        logger.info("Updating command status ...")
        update_result = await self.update_command(
            command.id,
            self.node_id,
            CommandStatusEnum.SUCCESS if result.is_ok() else CommandStatusEnum.FAILURE,
            result,
        )
        if update_result.is_err():
            err_msg = f"Failed to update command status: {update_result.unwrap_err()}"
            logger.error(err_msg)
            return update_result
        logger.debug(
            "CommandServiceLinux.execute - updated command status: %s",
            update_result.unwrap().model_dump_json(indent=4),
        )
        logger.info("Command status updated successfully.")
        return Ok(None)

    async def update_command(
        self,
        command_id: int,
        node_id: int,
        status: CommandStatusEnum,
        result: Optional[Result[str, str]] = None,
    ) -> Result[CommandNodeRelationship, str]:
        async with ApiClient(configuration=self.api_config) as api_client:
            commands_api = CommandsApi(api_client)
            try:
                logger.debug(
                    "CommandServiceLinux.update_command - \
command API and api client objs: %s, %s",
                    commands_api,
                    api_client,
                )
                updated_output = (
                    await commands_api.update_command_outputs_commands_outputs_put(
                        update_node_relationship=UpdateNodeRelationship(
                            command_id=command_id,
                            node_id=node_id,
                            status=status,
                            error=(
                                result.unwrap_err()
                                if (result and result.is_err())
                                else None
                            ),
                            output=(
                                result.unwrap() if (result and result.is_ok()) else None
                            ),
                        )
                    )
                )
                logger.debug(
                    "CommandServiceLinux.update_command - updated command: %s",
                    updated_output.model_dump_json(indent=4),
                )
                return Ok(updated_output)
            except Exception as e:
                err_msg = f"Failed to update command: {e}"
                logger.error(err_msg)
                return Err(err_msg)

    def run_command(self, command: Command) -> Result[str, str]:
        try:
            result = subprocess.run(
                command.command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=command.timeout,
            )
            logger.debug("CommandServiceLinux.run_command - result: %s", result)
            return Ok(result.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            err_msg = f"Command failed: [subprocess.CalledProcessError] - {e}"
            logger.error(err_msg)
            return Err(err_msg)
        except Exception as e:
            err_msg = f"Command failed: {e}"
            logger.error(err_msg)
            return Err(err_msg)
