"""Connection over CAN bus."""

import logging

import can

from .abc import RpcClient, RpcServer

logger = logging.getLogger(__name__)


class RpcClientCAN(RpcClient):
    """RPC connection to some SHV peer over CAN bus.

    :param bus: CAN bus to be used for the communication.
    :param local: The address to be used as the local one for this peer.
    :param dest: The address of the destination peer.
    """

    def __init__(self, interface: str, local: int, dest: int) -> None:
        self.interface = interface
        """CAN interfaces to be used."""
        self.local_address = local
        """Address used for this local peer's end (1-255)."""
        self.dest_address = dest
        """Address of the peer this connection should be connected to."""
        self._bus: can.Bus | None = None
        self._reader: can.AsyncBufferedReader
        self._notifier: can.Notifier

    def __str__(self) -> str:
        return f"can:{self.interface}:{self.local_address}:{self.dest_address}"

    async def _send(self, msg: bytes) -> None:
        if self._bus is None:
            raise EOFError("Not connected")
        self._bus.send(msg)
        # TODO exception?

    async def _receive(self) -> bytes:
        if self._bus is None:
            raise EOFError("Not connected")
        msg = await reader.get_message()
        # TODO we need to manage multiple messages

    async def reset(self) -> None:
        """Reset or establish the connection.

        This method not only resets the existing connection but primarilly
        estableshes the new one.
        """
        if not self.connected:
            self._bus = can.Bus(interface=self.interface, receive_own_messages=False)
            self._reader = can.AsyncBufferedReader()
            self._notifier = can.Notifier(self._bus, [self._reader])
            logger.debug("%s: Connected", self)
        else:
            await super().reset()

    @property
    def connected(self) -> bool:
        """Check if client is still connected."""
        return self._bus is not None and self._bus.state is not can.BusState.ERROR

    def _disconnect(self) -> None:
        if self._bus is not None:
            self._bus.shutdown()

    async def wait_disconnect(self) -> None:
        """Wait for the client's disconnection."""
        pass  # Nothing to wait for


class RpcServerCAN(RpcServer):
    """RPC server listening on CAN bus."""

    def __init__(self, bus: can.Bus, address: int) -> None:
        self.bus = bus
        self._address = address
