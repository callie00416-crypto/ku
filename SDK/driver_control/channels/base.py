from __future__ import annotations

from driver_control.analyzer.connection import AnalyzerConnection


class BusChannel:

    def __init__(self, analyzer: AnalyzerConnection) -> None:
        self.analyzer = analyzer

    def transact(self, payload: bytes, *, timeout_s: float | None = None) -> bytes:
        raise NotImplementedError(f"{type(self).__name__} does not implement transact()")
