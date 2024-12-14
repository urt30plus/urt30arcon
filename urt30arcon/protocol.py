import asyncio
import logging
from typing import Any, cast

logger = logging.getLogger(__name__)


class _Protocol(asyncio.DatagramProtocol):
    def __init__(
        self, recv_q: asyncio.Queue[bytes], buffer_free: asyncio.Event
    ) -> None:
        buffer_free.set()
        self._recv_q = recv_q
        self._buffer_free = buffer_free
        self._transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        logger.debug(transport)
        self._transport = cast("asyncio.DatagramTransport", transport)

    def connection_lost(self, exc: Exception | None) -> None:
        logger.debug("Connection closed: %r", exc)
        if size := self._recv_q.qsize():
            logger.debug("Receive queue has pending items: %s", size)
        if self._transport:
            self._transport.close()

    def datagram_received(self, data: bytes, _: tuple[str | Any, int]) -> None:
        logger.debug(data)
        self._recv_q.put_nowait(data)

    def error_received(self, exc: Exception) -> None:
        self.connection_lost(exc)

    def pause_writing(self) -> None:
        logger.debug("pausing writes")
        self._buffer_free.clear()

    def resume_writing(self) -> None:
        logger.debug("resuming writes")
        self._buffer_free.set()
