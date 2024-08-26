import json
from abc import ABC, abstractmethod
from typing import List, Literal

import psutil
from ambient_backend_api_client.models import InterfaceTypeEnum, NetworkInterface
from result import Ok

from ambient_edge_server.utils import logger


class InterfaceService(ABC):
    @abstractmethod
    async def get_network_interfaces(self) -> List[NetworkInterface]:
        """Get network interfaces on the device."""


class LinuxInterfaceService(InterfaceService):
    def __init__(self) -> None:
        self._running = False
        self._error = Ok("initialized")

    def determine_if_ipv4_or_ipv6(self, address: str) -> Literal["ipv4", "ipv6"]:
        # we could probably use something more sophisticated in the future
        if "." in address:
            return "ipv4"
        elif ":" in address:
            return "ipv6"
        raise ValueError(f"Address {address} is not a valid IPv4 or IPv6 address.")

    async def get_network_interfaces(self) -> List[NetworkInterface]:
        logger.info("Starting to fetch network interface details.")
        interfaces = psutil.net_if_addrs()
        logger.debug("Interfaces: %s", json.dumps(interfaces, indent=4))
        network_interfaces = []

        for interface_name, addresses in interfaces.items():
            logger.debug("Processing %s interface ...", interface_name)
            logger.debug("Addresses: %s", addresses)

            for addr in addresses:
                details = {
                    "name": f"{interface_name}-{addr.address}",
                    # Default to OTHER, adjust logic as needed
                    "type": InterfaceTypeEnum.UNKNOWN,
                }
                logger.debug("Address: %s", addr)
                ip_version = self.determine_if_ipv4_or_ipv6(addr.address)
                if ip_version == "ipv4":
                    details["ipv4_address"] = addr.address
                    details["netmask"] = addr.netmask
                else:
                    details["ipv6_address"] = addr.address
                details["broadcast"] = addr.broadcast

                # Interface type heuristic
                wifi_heuristics = ["wi-fi", "wifi", "wlan"]
                ethernet_heuristics = [
                    "eth",
                    "enp",
                    "ens",
                    "eno",
                    "enx",
                    "docker",
                    "lo",
                    "br",
                ]

                if any(
                    heuristic in interface_name.lower() for heuristic in wifi_heuristics
                ):
                    details["type"] = InterfaceTypeEnum.WIFI
                elif any(
                    heuristic in interface_name.lower()
                    for heuristic in ethernet_heuristics
                ):
                    details["type"] = InterfaceTypeEnum.ETHERNET

                network_interface = NetworkInterface(**details)
                logger.debug(
                    "Network Interface: %s", network_interface.model_dump_json(indent=4)
                )
                network_interfaces.append(network_interface)
            logger.info(f"Added {interface_name} to network interfaces.")

        logger.info("Completed fetching all network interfaces.")
        return network_interfaces
