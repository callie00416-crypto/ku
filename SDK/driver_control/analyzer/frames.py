from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Tuple


ENCODER_RETURN_DIRECT = 2
ENCODER_INTERFACE_RS485 = 3

class ControlType(IntEnum):
    GET = 0
    SET = 1
    DATA = 2


class DeviceType(IntEnum):
    ANALYZER = 0
    ENCODER = 1
    DRIVER = 2


class EncoderCommandType(IntEnum):
    STATUS = 0
    READOUT_CONFIG = 1
    READOUT = 2


class AnalyzerCommandType(IntEnum):
    FRAME_ID = 8
    MODE = 9
    DIRECT_DATA = 10


@dataclass(frozen=True)
class EncoderRequestInformation:
    package_id: int = 0
    request_id: int = 1
    reserved_u16: int = 0

    def to_bytes(self) -> bytes:
        return struct.pack(
            "<BBH",
            self.package_id & 0xFF,
            self.request_id & 0xFF,
            self.reserved_u16 & 0xFFFF,
        )


@dataclass(frozen=True)
class USBDataHeader:
    device: int
    control: int
    command: int
    buffer_bytes_length: int
    request_information: EncoderRequestInformation

    def to_bytes(self) -> bytes:
        cdev = ((self.control & 0x0F) << 4) | (self.device & 0x0F)
        return (
            struct.pack("<BBH", cdev, self.command & 0xFF, self.buffer_bytes_length & 0xFFFF)
            + self.request_information.to_bytes()
        )

    @staticmethod
    def unpack_first_byte(cdev: int) -> Tuple[int, int]:
        return cdev & 0x0F, (cdev >> 4) & 0x0F

    @classmethod
    def from_bytes(cls, raw: bytes) -> "USBDataHeader":
        if len(raw) != 8:
            raise ValueError(f"USB header must be 8 bytes, got {len(raw)}")
        cdev, command, body_length = struct.unpack("<BBH", raw[:4])
        device, control = cls.unpack_first_byte(cdev)
        req = EncoderRequestInformation(
            package_id=raw[4],
            request_id=raw[5],
            reserved_u16=struct.unpack_from("<H", raw, 6)[0],
        )
        return cls(device, control, command, body_length, req)


@dataclass(frozen=True)
class USBPacket:
    header: USBDataHeader
    body: bytes


@dataclass(frozen=True)
class EncoderReadout:
    config_index: int = 0
    times: int = 1
    delay_time_us: int = 10

    def to_bytes(self) -> bytes:
        return struct.pack(
            "<BBI",
            self.config_index & 0xFF,
            self.times & 0xFF,
            self.delay_time_us & 0xFFFFFFFF,
        )


@dataclass(frozen=True)
class EncoderReadoutConfig:
    interface: int
    return_type: int
    uart_command: int
    timeout_byte_num: int
    baud_rate: int
    followed_data_length: int
    reserved_u32: int
    followed_data: bytes

    def to_bytes(self) -> bytes:
        head = struct.pack(
            "<BBBBIII",
            self.interface & 0xFF,
            self.return_type & 0xFF,
            self.uart_command & 0xFF,
            self.timeout_byte_num & 0xFF,
            self.baud_rate & 0xFFFFFFFF,
            self.followed_data_length & 0xFFFFFFFF,
            self.reserved_u32 & 0xFFFFFFFF,
        )
        return head + self.followed_data


@dataclass(frozen=True)
class EncoderStatus:
    encoder_status: int
    start_trigger_without_delay: int
    start_trigger_frame: int
    usb_trigger_interval: int

    def to_bytes(self) -> bytes:
        return struct.pack(
            "<BBxxII",
            self.encoder_status & 0xFF,
            self.start_trigger_without_delay & 0xFF,
            self.start_trigger_frame & 0xFFFFFFFF,
            self.usb_trigger_interval & 0xFFFFFFFF,
        )


def build_usb_request(header: USBDataHeader, body: bytes = b"") -> bytes:
    actual = USBDataHeader(
        header.device,
        header.control,
        header.command,
        len(body),
        header.request_information,
    )
    return actual.to_bytes() + body


def frame_id_add(frame_body: bytes, increment: int = 5000) -> int:
    if len(frame_body) < 3:
        return 0
    current = frame_body[1] | (frame_body[2] << 8)
    target = current + increment
    return target - (1 << 14) if target > (1 << 14) - 1 else target


def parse_trigger_payload(body: bytes) -> Optional[bytes]:
    if len(body) < 4:
        return None
    _, word1 = struct.unpack_from("<HH", body, 0)
    length = (word1 >> 5) & 0x7FF
    if length <= 0 or 4 + length > len(body):
        return None
    return body[4 : 4 + length]

