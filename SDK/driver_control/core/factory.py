from __future__ import annotations

from typing import Any, Callable

from driver_control.analyzer.connection import AnalyzerConnection
from driver_control.devices.base import DeviceInstance
from driver_control.devices.encoder import EncoderDevice
from driver_control.devices.robot import RobotDevice
from driver_control.devices.servo import ServoDevice
from driver_control.protocols.RS485.Servo import Rs485ServoProtocol


ProtocolBuilder = Callable[[AnalyzerConnection, dict[str, Any]], object]
DeviceBuilder = Callable[[str, AnalyzerConnection, object, dict[str, Any]], DeviceInstance]


class DeviceFactory:
    def __init__(self) -> None:
        self._protocols: dict[str, ProtocolBuilder] = {
            "rs485-servo": self._build_rs485_servo,
        }
        self._devices: dict[str, DeviceBuilder] = {
            "generic": lambda device_id, analyzer, protocol, config: DeviceInstance(device_id, analyzer, protocol, config),
            "encoder": lambda device_id, analyzer, protocol, config: EncoderDevice(device_id, analyzer, protocol, config),
            "robot": lambda device_id, analyzer, protocol, config: RobotDevice(device_id, analyzer, protocol, config),
            "servo": lambda device_id, analyzer, protocol, config: ServoDevice(device_id, analyzer, protocol, config),
        }

    def register_protocol(self, name: str, builder: ProtocolBuilder) -> None:
        self._protocols[name] = builder

    def register_device(self, kind: str, builder: DeviceBuilder) -> None:
        self._devices[kind] = builder

    def create(self, config: dict[str, Any], analyzers: dict[str, AnalyzerConnection]) -> DeviceInstance:
        device_id = str(config["id"])
        kind = str(config.get("kind", "servo"))
        protocol_name = str(config.get("protocol", "rs485-servo"))
        analyzer_id = str(config["analyzer"])
        if analyzer_id not in analyzers:
            raise KeyError(f"unknown analyzer: {analyzer_id!r}")
        if protocol_name not in self._protocols:
            raise KeyError(f"unknown protocol: {protocol_name!r}")
        if kind not in self._devices:
            raise KeyError(f"unknown device kind: {kind!r}")
        analyzer = analyzers[analyzer_id]
        protocol = self._protocols[protocol_name](analyzer, config)
        return self._devices[kind](device_id, analyzer, protocol, config)

    @staticmethod
    def _build_rs485_servo(analyzer: AnalyzerConnection, config: dict[str, Any]) -> Rs485ServoProtocol:
        return Rs485ServoProtocol(
            analyzer,
            rs485_baud=int(config.get("rs485_baud", 2_500_000)),
            read_frequency_hz=int(config.get("read_frequency_hz", 4000)),
            default_transport=str(config.get("default_transport", "single-read")),
        )
