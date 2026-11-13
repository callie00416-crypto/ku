from __future__ import annotations

import struct
from typing import Any

from driver_control.channels.rs485.Servo import (
    DEFAULT_READ_FREQUENCY_HZ,
    DEFAULT_RS485_BAUD,
    ServoRs485PassthroughChannel,
    ServoRs485SingleReadChannel,
)
from driver_control.core.exceptions import CRCError, ProtocolError
from driver_control.protocols.RS485 import Rs485Protocol
from driver_control.protocols.crc import append_crc, check_crc
from .registers import REGISTERS


FC_READ = 0x01
FC_WRITE = 0x02


class Rs485ServoProtocol(Rs485Protocol):
    def __init__(
        self,
        analyzer,
        *,
        rs485_baud: int = DEFAULT_RS485_BAUD,
        read_frequency_hz: int = DEFAULT_READ_FREQUENCY_HZ,
        default_transport: str = "single-read",
    ) -> None:
        self.analyzer = analyzer
        self.rs485_baud = rs485_baud
        self.read_frequency_hz = read_frequency_hz
        self.single_read = ServoRs485SingleReadChannel(
            analyzer,
            rs485_baud=rs485_baud,
            read_frequency_hz=read_frequency_hz,
        )
        self.passthrough = ServoRs485PassthroughChannel(analyzer, rs485_baud=rs485_baud)
        self.default_transport = default_transport

    def read(self, node_id: int | None = None, **params: Any) -> Any:
        register = params.pop("register", None)
        if register is None:
            raise ValueError("RS485 servo read() requires register=<int>")
        return self.read_register(int(node_id if node_id is not None else 1), int(register), **params)

    def write(self, node_id: int | None = None, data: Any = None, **params: Any) -> Any:
        register = params.pop("register", None)
        if register is None:
            raise ValueError("RS485 servo write() requires register=<int>")
        return self.write_register(int(node_id if node_id is not None else 1), int(register), data, **params)

    def read_register(
        self,
        node_id: int,
        register: int,
        *,
        count: int = 1,
        timeout_s: float | None = None,
        transport: str | None = None,
    ) -> Any:
        frame = self._build_frame(node_id, FC_READ, register, count)
        response = self._channel(transport).transact(frame, timeout_s=timeout_s)
        values = self.parse_response(response)
        if count == 1:
            return values.get(register)
        return values

    def write_register(
        self,
        node_id: int,
        register: int,
        value: Any,
        *,
        data_type: str | None = None,
        timeout_s: float | None = None,
        transport: str | None = None,
    ) -> bytes:
        payload = encode_value(value, data_type or register_type(register))
        frame = self._build_frame(node_id, FC_WRITE, register, 1, payload)
        response = self._channel(transport).transact(frame, timeout_s=timeout_s)
        self.validate_response(response)
        return response

    def scan_nodes(
        self,
        *,
        start: int = 0,
        end: int = 30,
        timeout_s: float = 0.08,
        transport: str | None = None,
    ) -> list[int]:
        found: list[int] = []
        for node_id in range(start, end + 1):
            try:
                bus_id = self.read_register(node_id, 0x01, count=1, timeout_s=timeout_s, transport=transport)
            except Exception:
                continue
            if isinstance(bus_id, int):
                found.append(bus_id)
        return found

    def read_mcu_guid(
        self,
        node_id: int,
        *,
        timeout_s: float | None = None,
        transport: str | None = None,
    ) -> str | None:
        values = self.read_register(node_id, 0x22, count=3, timeout_s=timeout_s, transport=transport)
        if not isinstance(values, dict):
            return None
        parts = [values.get(0x22), values.get(0x23), values.get(0x24)]
        if any(part is None for part in parts):
            return None
        return "".join(f"{int(part) & 0xFFFFFFFF:08x}" for part in parts)

    def parse_response(self, frame: bytes) -> dict[int, Any]:
        self.validate_response(frame)
        start_register = frame[2]
        count = frame[3]
        expected_len = 4 + count * 4 + 1
        if len(frame) < expected_len:
            raise ProtocolError(f"short response: expected at least {expected_len} bytes, got {len(frame)}")
        values: dict[int, Any] = {}
        for offset in range(count):
            register = start_register + offset
            data_offset = 4 + offset * 4
            values[register] = decode_value(frame[data_offset : data_offset + 4], register_type(register))
        return values

    def validate_response(self, frame: bytes) -> None:
        if len(frame) < 5:
            raise ProtocolError(f"response too short: {frame.hex()}")
        if not check_crc(frame):
            raise CRCError(f"CRC mismatch: {frame.hex()}")

    def _channel(self, name: str | None):
        name = name or self.default_transport
        if name == "single-read":
            return self.single_read
        if name == "passthrough":
            return self.passthrough
        raise ValueError(f"unsupported transport: {name!r}")

    @staticmethod
    def _build_frame(node_id: int, function_code: int, register: int, count: int, data: bytes | None = None) -> bytes:
        header = bytes([node_id & 0xFF, function_code & 0xFF, register & 0xFF, count & 0xFF])
        return append_crc(header + (data or b""))


def register_type(register: int) -> str:
    return REGISTERS.get(register).type if register in REGISTERS else "float32"


def encode_value(value: Any, data_type: str) -> bytes:
    if data_type == "uint8":
        return struct.pack("<B", int(value) & 0xFF) + b"\x00\x00\x00"
    if data_type == "int8":
        return struct.pack("<b", int(value)) + b"\x00\x00\x00"
    if data_type == "uint16":
        return struct.pack("<H", int(value) & 0xFFFF) + b"\x00\x00"
    if data_type == "int16":
        return struct.pack("<h", int(value)) + b"\x00\x00"
    if data_type == "uint24":
        ivalue = int(value) & 0xFFFFFF
        return bytes([ivalue & 0xFF, (ivalue >> 8) & 0xFF, (ivalue >> 16) & 0xFF, 0])
    if data_type == "int32":
        return struct.pack("<i", int(value))
    if data_type == "float32":
        return struct.pack("<f", float(value))
    return struct.pack("<I", int(value) & 0xFFFFFFFF)


def decode_value(buffer: bytes, data_type: str) -> Any:
    data = buffer.ljust(4, b"\x00")
    if data_type == "uint8":
        return data[0]
    if data_type == "int8":
        return struct.unpack_from("<b", data, 0)[0]
    if data_type == "uint16":
        return struct.unpack_from("<H", data, 0)[0]
    if data_type == "int16":
        return struct.unpack_from("<h", data, 0)[0]
    if data_type == "uint24":
        return data[0] | (data[1] << 8) | (data[2] << 16)
    if data_type == "int32":
        return struct.unpack_from("<i", data, 0)[0]
    if data_type == "float32":
        return struct.unpack_from("<f", data, 0)[0]
    return struct.unpack_from("<I", data, 0)[0]


def build_modbus_uart(node_id: int, function_code: int, register: int, count: int, data: bytes | None = None) -> bytes:
    return Rs485ServoProtocol._build_frame(node_id, function_code, register, count, data)
