"""BLE client for the Kamoer X1 Pro V2.

The pump accepts one connection at a time, so each action opens a session
(connect, subscribe, startup frames, command, disconnect) and then releases it,
leaving the phone app free to connect in between.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from . import protocol as proto
from .const import REPLY_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class KamoerClient:
    def __init__(self, get_device: Callable[[], BLEDevice | None], name: str) -> None:
        self._get_device = get_device
        self._name = name
        self._lock = asyncio.Lock()
        self.volume_ml = 0.0
        self.last_reply: str | None = None
        self.last_error: str | None = None
        self._listeners: list[Callable[[], None]] = []

    def add_listener(self, cb: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(cb)
        return lambda: self._listeners.remove(cb)

    def _notify(self) -> None:
        for cb in list(self._listeners):
            cb()

    async def start(self) -> None:
        # Sends the volume first so a start always doses the number shown in HA.
        await self._session([("set volume", proto.set_volume_body(self.volume_ml)),
                             ("start", proto.START_RUN_BODY)])

    async def stop(self) -> None:
        await self._session([("stop", proto.STOP_RUN_BODY)])

    async def poll(self) -> None:
        await self._session([("status", proto.STATUS_BODY)])

    async def _session(self, commands: list[tuple[str, bytes]]) -> None:
        device = self._get_device()
        if device is None:
            self.last_error = "pump not in Bluetooth range"
            self._notify()
            raise ConnectionError(self.last_error)
        async with self._lock:
            replies: asyncio.Queue[bytes] = asyncio.Queue()

            def on_notify(_char, data: bytearray) -> None:
                replies.put_nowait(bytes(data))

            client: BleakClient = await establish_connection(
                BleakClientWithServiceCache, device, self._name)
            try:
                await client.start_notify(proto.NOTIFY_UUID, on_notify)
                seq, counter = 0, proto.FIRST_COUNTER
                steps = [("startup", b) for b in proto.startup_bodies()] + commands
                for label, body in steps:
                    frame = proto.build_frame(seq, counter, body)
                    _LOGGER.debug("%s: write %s", label, frame.hex())
                    await client.write_gatt_char(proto.WRITE_UUID, frame, response=True)
                    seq += 1
                    counter += 1
                    try:
                        data = await asyncio.wait_for(replies.get(), REPLY_TIMEOUT)
                        self.last_reply = data.hex()
                        _LOGGER.debug("%s: reply %s", label, self.last_reply)
                    except asyncio.TimeoutError:
                        _LOGGER.warning("%s: no reply from pump", label)
                self.last_error = None
            except Exception as err:
                self.last_error = str(err)
                raise
            finally:
                try:
                    await client.disconnect()
                finally:
                    self._notify()
