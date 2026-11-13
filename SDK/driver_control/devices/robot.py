from __future__ import annotations

from typing import Any

from driver_control.devices.base import DeviceInstance


class RobotDevice(DeviceInstance):
    def command(self, name: str, **params: Any) -> Any:
        return self.write(command=name, **params)
