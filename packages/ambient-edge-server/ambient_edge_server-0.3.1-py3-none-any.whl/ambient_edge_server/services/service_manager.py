from ambient_backend_api_client import Configuration
from ambient_event_bus_client import Client, ClientOptions
from docker import DockerClient

from ambient_edge_server.config import settings
from ambient_edge_server.repos.node_repo import FileNodeRepo
from ambient_edge_server.repos.system_daemon_repo import LinuxSystemDaemonRepo
from ambient_edge_server.repos.token_repo import EncryptedTokenRepository
from ambient_edge_server.services import (
    authorization_service,
    command_service,
    crud_service,
    event_service,
    handler_service,
    health_service,
    interface_service,
    port_service,
    registry_service,
    system_daemon_service,
)
from ambient_edge_server.utils import logger


class ServiceManager:
    def __init__(self):
        if settings.platform == "linux":
            self._system_daemon_repo = LinuxSystemDaemonRepo()
            self._system_daemon_service = system_daemon_service.LinuxDaemonService(
                self._system_daemon_repo
            )
            self._interface_service = interface_service.LinuxInterfaceService()
        else:
            logger.error("Platform not supported")
            raise NotImplementedError("Platform not supported")
        self._port_service = port_service.PortService()
        self._token_repo = EncryptedTokenRepository()
        self._node_repo = FileNodeRepo()
        self._authorization_service = authorization_service.AuthorizationService(
            token_repo=self._token_repo, node_repo=self._node_repo
        )

        self._event_client = Client(
            ClientOptions(
                event_api_url=settings.event_bus_api,
                connection_service_url=settings.connection_service_url,
                api_token="dummy_token",
                log_level=settings.ambient_log_level,
            )
        )
        self._event_service = event_service.AmbientBusEventService(
            client=self._event_client, node_repo=self._node_repo
        )

        self._docker_client = DockerClient()
        self._registry_svc_factory = registry_service.RegistryServiceFactory(
            docker_client=self._docker_client,
            auth_svc=self._authorization_service,
        )
        if settings.platform == "linux":
            self._command_service = command_service.CommandServiceLinux(
                node_repo=self._node_repo
            )
        self._handler_service = handler_service.HandlerService(
            self._event_service,
            docker_client=self._docker_client,
            registry_svc_factory=self._registry_svc_factory,
            cmd_svc=self._command_service,
        )

        # Keep Health Service at the bottom since
        # it should be able to access all other services
        if settings.platform == "linux":
            self._health_service = health_service.LinuxHealthService(
                node_repo=self._node_repo,
                event_service=self._event_service,
                auth_service=self._authorization_service,
                interface_service=self._interface_service,
                interval_minutes=5,
            )

        self._crud_service = crud_service.CRUDService(node_repo=self._node_repo)

    async def init(self):
        await self._port_service.init()

        token = await self._authorization_service.get_token()
        if not token:
            logger.error("Failed to get token")
            return
        logger.debug("got token [ %d chars ]", len(token))
        self._event_client.token = token
        await self._event_client.init_client()
        await self._event_service.start()
        await self._handler_service.start()

        api_config = Configuration(
            host=settings.backend_api_url,
            access_token=token,
        )
        await self._health_service.start(api_config=api_config)
        await self._crud_service.init(api_config=api_config)
        await self._registry_svc_factory.init()
        await self._command_service.init(api_config=api_config)

    def get_port_service(self):
        return self._port_service

    def get_authorization_service(self):
        return self._authorization_service

    def get_event_service(self):
        return self._event_service

    def get_system_daemon_service(self):
        return self._system_daemon_service

    def get_interface_service(self):
        return self._interface_service

    def get_crud_service(self):
        return self._crud_service

    def get_health_service(self):
        return self._health_service


svc_manager = ServiceManager()
