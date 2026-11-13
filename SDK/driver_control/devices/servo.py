from __future__ import annotations

from typing import Any

from driver_control.devices.base import DeviceInstance


class ServoDevice(DeviceInstance):
    @property
    def node_id(self) -> int:
        return int(self.config.get("node_id", 1))

    def read(self, **params: Any):
        if "register" in params:
            register = int(params.pop("register"))
            count = int(params.pop("count", 1))
            return self.read_register(register, count=count, **params)
        return super().read(**params)

    def write(self, data: Any = None, **params: Any):
        if "register" in params:
            register = int(params.pop("register"))
            return self.write_register(register, data, **params)
        return super().write(data, **params)

    def read_register(
        self,
        reg: int,
        *,
        count: int = 1,
        timeout: float | None = None,
        transport: str | None = None,
    ):
        return self.protocol.read_register(
            self.node_id,
            reg,
            count=count,
            timeout_s=timeout,
            transport=transport,
        )

    def write_register(
        self,
        reg: int,
        value: Any,
        *,
        data_type: str | None = None,
        timeout: float | None = None,
        transport: str | None = None,
    ):
        return self.protocol.write_register(
            self.node_id,
            reg,
            value,
            data_type=data_type,
            timeout_s=timeout,
            transport=transport,
        )

    def scan_nodes(
        self,
        start: int = 0,
        end: int = 30,
        *,
        timeout: float = 0.08,
        transport: str | None = None,
    ) -> list[int]:
        scanner = getattr(self.protocol, "scan_nodes")
        return scanner(start=start, end=end, timeout_s=timeout, transport=transport)

    def read_mcu_guid(
        self,
        node_id: int | None = None,
        *,
        timeout: float | None = None,
        transport: str | None = None,
    ) -> str | None:
        reader = getattr(self.protocol, "read_mcu_guid", None)
        if reader is None:
            return None
        return reader(self.node_id if node_id is None else node_id, timeout_s=timeout, transport=transport)

