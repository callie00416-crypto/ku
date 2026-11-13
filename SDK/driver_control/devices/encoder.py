from __future__ import annotations

from typing import Any

from driver_control.devices.base import DeviceInstance


class EncoderDevice(DeviceInstance):
    def read_position(self, **params: Any) -> Any:
        return self.read(kind="position", **params)
