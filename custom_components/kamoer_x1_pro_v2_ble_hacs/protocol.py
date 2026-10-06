"""Kamoer X1 Pro V2 BLE wire protocol (reverse-engineered from an HCI snoop capture).

GATT: vendor service 0xFFFF, write characteristic 0xFF01, notify characteristic 0xFF02.
Frames written to FF01:   4d 00 <seq> <len> <counter:u16le> <body...>
Frames notified on FF02:  4d 04 <seq> <len> <counter:u16le> <body...>
`len` is the number of bytes after it (counter + body). `seq` counts up from 0 on
every connection and the pump expects the three startup frames first.

Only frames seen in the capture are verified. Dose start/stop are NOT: see
START_RUN_BODY / STOP_RUN_BODY.
"""
from __future__ import annotations

import struct

SERVICE_UUID = "0000ffff-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"

WRITE_MAGIC = b"\x4d\x00"
NOTIFY_MAGIC = b"\x4d\x04"
FIRST_COUNTER = 0x0239  # the app's first counter value; the pump accepted it from a fresh session

# Bodies (the bytes after the 16-bit counter) seen in the capture.
HELLO_BODY = bytes.fromhex("00010001000100")
INFO_BODY = bytes.fromhex("000000000002")
POLL_BODY = bytes.fromhex("0002000100040100")
STATUS_BODY = bytes.fromhex("000000000004")
SET_VOLUME_PREFIX = bytes.fromhex("000a000100030001")
# UNVERIFIED: sent by the app on every calibration run. Believed to be "run".
START_RUN_BODY = bytes.fromhex("0002000100130100")
# UNVERIFIED GUESS: START_RUN with the enable word cleared (mirrors the old MQTT stop frame).
STOP_RUN_BODY = bytes.fromhex("0002000100130000")


def build_frame(seq: int, counter: int, body: bytes) -> bytes:
    payload = struct.pack("<H", counter & 0xFFFF) + body
    return WRITE_MAGIC + bytes([seq & 0xFF, len(payload)]) + payload


def set_volume_body(volume: float) -> bytes:
    """Body of the 'set value' write: command header, big-endian float32, 4 zero bytes."""
    return SET_VOLUME_PREFIX + struct.pack(">f", float(volume)) + b"\x00\x00\x00\x00"


def startup_bodies() -> list[bytes]:
    """The three frames the app sends before anything else."""
    return [HELLO_BODY, INFO_BODY, POLL_BODY]


class Notification:
    """A parsed FF02 notification. The body is kept raw; fields are not decoded yet."""

    def __init__(self, seq: int, counter: int, body: bytes) -> None:
        self.seq, self.counter, self.body = seq, counter, body

    def __repr__(self) -> str:
        return f"Notification(seq={self.seq}, counter={self.counter:#06x}, body={self.body.hex()})"


def parse_notification(data: bytes) -> Notification | None:
    if len(data) < 6 or data[:2] != NOTIFY_MAGIC:
        return None
    seq, length = data[2], data[3]
    payload = data[4:4 + length]
    if len(payload) < 2:
        return None
    return Notification(seq, struct.unpack("<H", payload[:2])[0], payload[2:])
