from __future__ import annotations

import queue
import threading
import time
from contextlib import contextmanager
from typing import Callable, Iterator, Optional

try:
    import serial
except ImportError:
    serial = None

from driver_control.analyzer.frames import (
    AnalyzerCommandType,
    ControlType,
    DeviceType,
    EncoderRequestInformation,
    USBDataHeader,
    USBPacket,
    build_usb_request,
)
from driver_control.core.exceptions import AnalyzerClosedError, AnalyzerTimeoutError


Predicate = Callable[[USBPacket], bool]
PacketCallback = Callable[[USBPacket], None]


class AnalyzerConnection:

    def __init__(
        self,
        port: str,
        *,
        serial_number: Optional[int] = None,
        serial_baud: int = 115200,
        serial_factory: Optional[Callable[..., object]] = None,
        read_timeout: float = 0.001,
    ) -> None:
        self.port = port
        self.serial_number = serial_number
        self.serial_baud = serial_baud
        self.read_timeout = read_timeout
        self._serial_factory = serial_factory
        self._serial = None
        self._packets: "queue.Queue[USBPacket]" = queue.Queue()
        self._transaction_lock = threading.RLock()
        self._request_lock = threading.Lock()
        self._request_id = 0
        self._stop_event = threading.Event()
        self._reader: Optional[threading.Thread] = None
        self._last_error: Optional[BaseException] = None

    @property
    def is_open(self) -> bool:
        return self._serial is not None and not self._stop_event.is_set()

    def open(self) -> "AnalyzerConnection":
        if self.is_open:
            return self
        if self._serial_factory is not None:
            self._serial = self._serial_factory(self.port, baudrate=self.serial_baud, timeout=self.read_timeout)
        else:
            if serial is None:
                raise RuntimeError("pyserial is required to open Analyzer serial ports")
            self._serial = serial.Serial(self.port, baudrate=self.serial_baud, timeout=self.read_timeout)
        self._stop_event.clear()
        self._reset_buffers()
        self._reader = threading.Thread(target=self._read_loop, name=f"AnalyzerReader-{self.port}", daemon=True)
        self._reader.start()
        return self

    def close(self) -> None:
        self._stop_event.set()
        reader = self._reader
        if reader is not None and reader.is_alive():
            reader.join(timeout=0.5)
        if self._serial is not None:
            try:
                self._serial.close()
            finally:
                self._serial = None
        self._reader = None

    def __enter__(self) -> "AnalyzerConnection":
        return self.open()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        self.open()
        with self._transaction_lock:
            self.clear_pending_packets()
            yield

    def clear_pending_packets(self) -> None:
        while True:
            try:
                self._packets.get_nowait()
            except queue.Empty:
                return

    def reset_buffers(self) -> None:
        self.clear_pending_packets()
        self._reset_buffers()

    def set_mode(
        self,
        body: bytes,
        *,
        timeout_s: float | None = None,
        wait_ack: bool = False,
        delay_s: float = 0.2,
        reset_buffers: bool = True,
    ) -> int:
        timeout_s = 0.5 if timeout_s is None else timeout_s
        with self.transaction():
            rid = self.send_usb(DeviceType.ANALYZER, ControlType.SET, AnalyzerCommandType.MODE, body)
            if wait_ack:
                self.wait_ack(DeviceType.ANALYZER, rid, timeout_s)
            if delay_s > 0:
                time.sleep(delay_s)
            if reset_buffers:
                self.reset_buffers()
            return rid

    def enter_rs485_direct_mode(
        self,
        *,
        baud_rate: int = 2_500_000,
        timeout_s: float | None = None,
        delay_s: float = 0.2,
        wait_ack: bool = False,
        reset_buffers: bool = True,
    ) -> int:
        body = b"\x01" + int(baud_rate).to_bytes(3, "big") + b"\x50"
        return self.set_mode(
            body,
            timeout_s=timeout_s,
            wait_ack=wait_ack,
            delay_s=delay_s,
            reset_buffers=reset_buffers,
        )

    def enter_normal_mode(
        self,
        *,
        timeout_s: float | None = None,
        delay_s: float = 0.2,
        wait_ack: bool = False,
        reset_buffers: bool = True,
    ) -> int:
        return self.set_mode(
            b"\x00",
            timeout_s=timeout_s,
            wait_ack=wait_ack,
            delay_s=delay_s,
            reset_buffers=reset_buffers,
        )

    def send_usb(self, device: int, control: int, command: int, body: bytes = b"") -> int:
        ser = self._require_serial()
        request_id = self._next_request_id()
        header = USBDataHeader(
            device=device,
            control=control,
            command=command,
            buffer_bytes_length=len(body),
            request_information=EncoderRequestInformation(request_id=request_id),
        )
        ser.write(build_usb_request(header, body))
        ser.flush()
        return request_id

    def wait_packet(
        self,
        predicate: Predicate,
        timeout_s: float,
        *,
        on_unmatched: PacketCallback | None = None,
    ) -> USBPacket:
        deadline = time.monotonic() + timeout_s
        while True:
            self._raise_reader_error_if_needed()
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AnalyzerTimeoutError(f"timeout waiting for packet on {self.port}")
            try:
                packet = self._packets.get(timeout=min(remaining, 0.05))
            except queue.Empty:
                continue
            if predicate(packet):
                return packet
            if on_unmatched is not None:
                on_unmatched(packet)

    def wait_ack(self, device: int, request_id: int, timeout_s: float) -> USBPacket:
        return self.wait_packet(
            lambda p: p.header.device == device
            and p.header.request_information.request_id == request_id
            and p.header.control in (0, 1),
            timeout_s,
        )

    def _next_request_id(self) -> int:
        with self._request_lock:
            self._request_id = (self._request_id + 1) & 0xFF
            if self._request_id == 0:
                self._request_id = 1
            return self._request_id

    def _require_serial(self):
        if self._serial is None:
            raise AnalyzerClosedError(f"Analyzer {self.port} is not open")
        return self._serial

    def _reset_buffers(self) -> None:
        if self._serial is None:
            return
        for name in ("reset_input_buffer", "reset_output_buffer"):
            method = getattr(self._serial, name, None)
            if method:
                method()

    def _read_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                header_raw = self._read_exact(8)
                if header_raw is None:
                    continue
                header = USBDataHeader.from_bytes(header_raw)
                body = self._read_exact(header.buffer_bytes_length) if header.buffer_bytes_length else b""
                if body is None:
                    continue
                self._packets.put(USBPacket(header, body))
            except Exception as exc:
                self._last_error = exc
                time.sleep(0.01)

    def _read_exact(self, size: int) -> Optional[bytes]:
        if size == 0:
            return b""
        ser = self._require_serial()
        data = bytearray()
        while len(data) < size and not self._stop_event.is_set():
            chunk = ser.read(size - len(data))
            if chunk:
                data.extend(chunk)
            else:
                if not data:
                    return None
                time.sleep(0.001)
        return bytes(data) if len(data) == size else None

    def _raise_reader_error_if_needed(self) -> None:
        if self._last_error is not None:
            error = self._last_error
            self._last_error = None
            raise error
