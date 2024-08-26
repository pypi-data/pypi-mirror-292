import json

from ambient_backend_api_client import Command, EventLabel
from ambient_event_bus_client import Message

from ambient_edge_server.event_handlers.base_handler import BaseHandler
from ambient_edge_server.services.command_service import CommandService
from ambient_edge_server.services.event_service import EventService
from ambient_edge_server.utils import logger


class RunCommandHandler(BaseHandler):
    def __init__(self, event_svc: EventService, cmd_svc: CommandService) -> None:
        super().__init__(event_svc)
        self.cmd_svc = cmd_svc
        logger.debug("RunCommandHanlder initialized.")

    @property
    def label(self) -> EventLabel:
        return EventLabel.RUN_COMMAND_REQUESTED

    async def handle(self, msg: Message) -> None:
        try:
            logger.info("Handling message for topic: %s", msg.topic)

            msg_data: dict = json.loads(msg.message)
            logger.debug(
                "RunCommandHanlder.handle - msg_data: %s",
                json.dumps(msg_data, indent=4),
            )

            cmd = Command.model_validate(msg_data)
            logger.debug("RunCommandHanlder.handle - cmd: %s", cmd)

            result = await self.cmd_svc.execute(cmd)
            logger.debug("RunCommandHanlder.handle - result: %s", result)

            logger.info(
                "Command executed %s",
                ("successfully" if result.is_ok() else "unsuccessfully"),
            )
        except Exception as e:
            logger.error("Error handling message: %s", e)
