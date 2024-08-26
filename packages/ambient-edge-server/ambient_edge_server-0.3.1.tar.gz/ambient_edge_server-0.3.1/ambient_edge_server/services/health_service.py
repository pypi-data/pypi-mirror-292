import asyncio
import datetime
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Set

from ambient_backend_api_client import (
    ApiClient,
    AppApiModelsNodeStatusEnum,
    Configuration,
    NodesApi,
)
from result import Err, Ok, Result

from ambient_edge_server.repos.node_repo import NodeRepo
from ambient_edge_server.services.authorization_service import AuthorizationService
from ambient_edge_server.services.event_service import EventService
from ambient_edge_server.services.interface_service import InterfaceService
from ambient_edge_server.utils import logger


class HealthService(ABC):
    @abstractmethod
    async def start(self):
        """Start the service."""

    @abstractmethod
    async def stop(self):
        """Stop the service."""

    @abstractmethod
    async def get_health(self) -> str:
        """Get the health of the service."""

    @abstractmethod
    async def run_system_sweep(self) -> str:
        """Run a system sweep and update backend with results."""

    @property
    @abstractmethod
    def interval_min(self) -> int:
        """Get the interval in minutes for the system sweep."""


class LinuxHealthService(HealthService):
    def __init__(
        self,
        node_repo: NodeRepo,
        event_service: EventService,
        auth_service: AuthorizationService,
        interface_service: InterfaceService,
        interval_minutes: int = 5,
    ):
        self.node_repo = node_repo
        self.event_service = event_service
        self.auth_service = auth_service
        self.interface_service = interface_service
        self._interval_min_ = interval_minutes

        self.api_config: Optional[Configuration] = None
        self._running = False
        self._tasks: Set[asyncio.Task] = set()

    async def start(self, api_config: Configuration):
        self.api_config = api_config
        self._running = True
        sys_sweep_task = asyncio.create_task(self._system_sweep_task())
        sys_sweep_task.add_done_callback(self._handleDoneTask)
        self._tasks.add(sys_sweep_task)

    async def stop(self):
        self._running = False
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    async def get_health(self) -> Result[str, str]:
        if not self._running:
            return Err("Service not running")
        if len(self._tasks) == 0:
            return Err("No health tasks running")
        return Ok("OK")

    async def run_system_sweep(self) -> Result[str, str]:
        logger.info("Running system sweep ...")
        if (await self.get_health()).is_err():
            return Err("Health check failed")

        if not self.event_service.is_running or self.event_service.error:
            logger.error(
                "Event service not running or in error state.\n\
  is_running: %s\n    error: %s",
                self.event_service.is_running,
                self.event_service.error,
            )
            return Err("Event service not running or in error state")

        if (await self.auth_service.verify_authorization_status()).is_err():
            logger.error("Node is not authorized with backend")
            return Err("Node is not authorized with backend")

        logger.info("System sweep completed successfully")
        return Ok("System sweep completed successfully")

    @property
    def interval_min(self) -> int:
        return self._interval_min_

    def _get_api_session(self) -> ApiClient:
        if not self.api_config:
            raise ValueError("API Configuration not set")
        return ApiClient(configuration=self.api_config)

    async def _system_sweep_task(self):
        while True:
            try:
                logger.debug("waiting for system sweep interval delay ... ")
                await asyncio.sleep(self._interval_min_ * 60)
                logger.debug("running system sweep ...")
                result = await self.run_system_sweep()
            except Exception as e:
                logger.error("error running system sweep: %s", str(e))
                result = Err(str(e))
            finally:
                logger.info("result of system sweep: %s", result)
                logger.debug("handling system sweep result ...")
                await self._handle_system_sweep_result(result)

    async def trigger_check_in(self):
        result = await self.run_system_sweep()
        await self._handle_system_sweep_result(result)

    async def _handle_system_sweep_result(self, result: Result[str, str]):
        last_seen = datetime.datetime.now().isoformat()
        current_interfaces = await self.interface_service.get_network_interfaces()
        interfaces = [i.model_dump_json(indent=4) for i in current_interfaces]
        if result.is_ok():
            logger.debug("updating backend with system sweep results ...")
            await self._patch_node(
                {
                    "last_seen": last_seen,
                    "status": AppApiModelsNodeStatusEnum.ACTIVE.value,
                    "interfaces": interfaces,
                }
            )
        else:
            await self._patch_node(
                {
                    "last_seen": last_seen,
                    "status": AppApiModelsNodeStatusEnum.ERROR.value,
                    "error": result.unwrap_err(),
                    "interfaces": interfaces,
                }
            )

    async def _patch_node(self, data: Dict[str, Any]) -> Result[str, str]:
        logger.info("Patching node with data: %s", json.dumps(data, indent=4))
        node_id = self.node_repo.get_node_id()
        logger.debug("Node ID: %s", node_id)

        async with self._get_api_session() as session:
            logger.debug("Patching node ...")
            logger.debug("session: %s", session)
            nodes_api = NodesApi(session)
            logger.debug("nodes_api: %s", nodes_api)
            try:
                patched_node = await nodes_api.update_node_nodes_node_id_patch(
                    node_id=node_id, body=data
                )
                logger.debug("Patched node: %s", patched_node.model_dump_json(indent=4))
                return Ok(f"Node {patched_node.name} patched successfully.")
            except Exception as e:
                logger.error("Error patching node: %s", str(e))
                return Err(f"Error patching node: {str(e)}")

    def _handleDoneTask(self, task: asyncio.Task):
        logger.debug("Handling task completion ...")
        self._tasks.remove(task)
        sys_sweep_task = asyncio.create_task(self._system_sweep_task())
        sys_sweep_task.add_done_callback(self._handleDoneTask)
        self._tasks.add(sys_sweep_task)
