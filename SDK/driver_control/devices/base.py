from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from driver_control.analyzer.connection import AnalyzerConnection


@dataclass
class DeviceInstance:
    id: str
    analyzer: AnalyzerConnection
    protocol: object
    config: dict[str, Any]

    @property
    def node_id(self) -> int | None:
        node = self.config.get("node_id")
        return None if node is None else int(node)

    def read(self, **params: Any) -> Any:
        reader = getattr(self.protocol, "read", None)
        if reader is None:
            raise NotImplementedError(f"{type(self.protocol).__name__} does not implement read()")
        return reader(self.node_id, **params)

    def write(self, data: Any = None, **params: Any) -> Any:
        writer = getattr(self.protocol, "write", None)
        if writer is None:
            raise NotImplementedError(f"{type(self.protocol).__name__} does not implement write()")
        return writer(self.node_id, data, **params)

    def scan_nodes(self, **params: Any) -> list[int]:
        scanner = getattr(self.protocol, "scan_nodes", None)
        if scanner is None:
            raise NotImplementedError(f"{type(self.protocol).__name__} does not implement scan_nodes()")
        return scanner(**params)
