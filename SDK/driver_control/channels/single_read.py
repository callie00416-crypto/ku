from __future__ import annotations

from abc import ABC, abstractmethod

from driver_control.channels.base import BusChannel


class SingleReadChannel(BusChannel, ABC):
    @abstractmethod
    def transact(self, payload: bytes, *, timeout_s: float | None = None) -> bytes:
        ...
