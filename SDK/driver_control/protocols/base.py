from __future__ import annotations

from typing import Any


class ProductProtocol:
    def read(self, node_id: int | None = None, **params: Any) -> Any:
        raise NotImplementedError(f"{type(self).__name__} does not implement generic read()")

    def write(self, node_id: int | None = None, data: Any = None, **params: Any) -> Any:
        raise NotImplementedError(f"{type(self).__name__} does not implement generic write()")

    def read_register(
        self,
        node_id: int,
        register: int,
        *,
        count: int = 1,
        timeout_s: float | None = None,
        transport: str | None = None,
    ) -> Any:
        raise NotImplementedError(f"{type(self).__name__} does not implement read_register()")

    def write_register(
        self,
        node_id: int,
        register: int,
        value: Any,
        *,
        data_type: str | None = None,
        timeout_s: float | None = None,
        transport: str | None = None,
    ) -> Any:
        raise NotImplementedError(f"{type(self).__name__} does not implement write_register()")

    def scan_nodes(
        self,
        *,
        start: int = 0,
        end: int = 30,
        timeout_s: float = 0.08,
        transport: str | None = None,
    ) -> list[int]:
        raise NotImplementedError(f"{type(self).__name__} does not implement scan_nodes()")
