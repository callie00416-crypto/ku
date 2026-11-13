from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional

try:
    import serial.tools.list_ports
except ImportError:
    serial = None

from driver_control.analyzer.connection import AnalyzerConnection


ANALYZER_VID = 0x6B6B
ANALYZER_PID = 0x0001
DEFAULT_SERIAL_BAUD = 115200


@dataclass(frozen=True)
class AnalyzerInfo:
    serial_number: int
    port: str
    description: str = ""


class AnalyzerManager:
    def __init__(self, *, serial_factory=None) -> None:
        self.serial_factory = serial_factory

    @staticmethod
    def discover() -> list[AnalyzerInfo]:
        if serial is None:
            raise RuntimeError("pyserial is required to discover Analyzer devices")
        out: list[AnalyzerInfo] = []
        for port in serial.tools.list_ports.comports():
            if port.vid == ANALYZER_VID and port.pid == ANALYZER_PID:
                sn = int(port.serial_number) if (port.serial_number or "").isdigit() else -1
                out.append(AnalyzerInfo(sn, port.device, getattr(port, "description", "") or ""))
        return out

    scan = discover

    def open_all(self, configs: Iterable[dict[str, Any]]) -> dict[str, AnalyzerConnection]:
        connections: dict[str, AnalyzerConnection] = {}
        discovered_by_sn = {str(i.serial_number): i for i in self.discover()} if self.serial_factory is None else {}
        for index, cfg in enumerate(configs):
            analyzer_id = str(cfg.get("id") or cfg.get("serial_number") or cfg.get("port") or f"analyzer_{index}")
            port = cfg.get("port")
            serial_number: Optional[int] = cfg.get("serial_number")
            if port is None and serial_number is not None:
                info = discovered_by_sn.get(str(serial_number))
                if info is None:
                    raise ValueError(f"Analyzer serial_number={serial_number} was not discovered")
                port = info.port
            if port is None:
                raise ValueError(f"Analyzer config {analyzer_id!r} must provide port or serial_number")
            conn = AnalyzerConnection(
                str(port),
                serial_number=serial_number,
                serial_baud=int(cfg.get("serial_baud", DEFAULT_SERIAL_BAUD)),
                serial_factory=self.serial_factory,
            ).open()
            connections[analyzer_id] = conn
        return connections
