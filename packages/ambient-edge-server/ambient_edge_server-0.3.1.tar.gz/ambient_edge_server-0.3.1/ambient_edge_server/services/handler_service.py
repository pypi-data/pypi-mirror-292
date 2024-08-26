from typing import List

from docker import DockerClient

from ambient_edge_server.event_handlers.authorize_to_registry_handler import (
    AuthorizeRegistryHandler,
)
from ambient_edge_server.event_handlers.base_handler import BaseHandler
from ambient_edge_server.event_handlers.deploy_service_handler import (
    DeployServiceHandler,
)
from ambient_edge_server.event_handlers.run_command_handler import RunCommandHandler
from ambient_edge_server.event_handlers.test_handler import TestHandler
from ambient_edge_server.services.command_service import CommandService
from ambient_edge_server.services.event_service import EventService
from ambient_edge_server.services.registry_service import RegistryServiceFactory


class HandlerService:
    def __init__(
        self,
        event_service: EventService,
        docker_client: DockerClient,
        registry_svc_factory: RegistryServiceFactory,
        cmd_svc: CommandService,
    ) -> None:
        self._handlers: List[BaseHandler] = [
            TestHandler(event_service),
            DeployServiceHandler(event_service, docker_client=docker_client),
            AuthorizeRegistryHandler(
                event_svc=event_service, registry_svc_factory=registry_svc_factory
            ),
            RunCommandHandler(event_svc=event_service, cmd_svc=cmd_svc),
        ]

    async def start(self):
        for handler in self._handlers:
            await handler.subscribe()

    def get_handlers(self):
        return self._handlers
