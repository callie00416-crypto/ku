from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from driver_control.analyzer.connection import AnalyzerConnection
from driver_control.analyzer.manager import AnalyzerInfo, AnalyzerManager
from driver_control.core.factory import DeviceFactory
from driver_control.devices.base import DeviceInstance


class ControlSystem:
    def __init__(
        self,
        *,
        analyzers: dict[str, AnalyzerConnection],
        devices: dict[str, DeviceInstance],
        factory: DeviceFactory | None = None,
    ) -> None:
        self.analyzers = analyzers
        self.devices = devices
        self.factory = factory or DeviceFactory()

    @classmethod
    def from_config(cls, config: dict[str, Any], *, serial_factory=None) -> "ControlSystem":
        manager = AnalyzerManager(serial_factory=serial_factory)
        analyzers = manager.open_all(config.get("analyzers", []))
        factory = DeviceFactory()
        devices: dict[str, DeviceInstance] = {}
        for device_config in config.get("devices", []):
            device = factory.create(device_config, analyzers)
            devices[device.id] = device
        return cls(analyzers=analyzers, devices=devices, factory=factory)

    @staticmethod
    def scan_analyzers() -> list[AnalyzerInfo]:
        return AnalyzerManager.discover()

    def scan_nodes(self, device_id: str, **params: Any) -> list[int]:
        return self.devices[device_id].scan_nodes(**params)

    def by_analyzer(self, analyzer_id: str) -> list[DeviceInstance]:
        return [device for device in self.devices.values() if device.config.get("analyzer") == analyzer_id]

    @classmethod
    def from_yaml(cls, path: str | Path, *, serial_factory=None) -> "ControlSystem":
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("PyYAML is required for ControlSystem.from_yaml()") from exc
        with open(path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh) or {}
        return cls.from_config(config, serial_factory=serial_factory)

    def close(self) -> None:
        for analyzer in self.analyzers.values():
            analyzer.close()

    def __enter__(self) -> "ControlSystem":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def run_parallel(
        self,
        calls: Mapping[str, Callable[[], Any]] | Iterable[Callable[[], Any] | tuple[str, Callable[[], Any]]],
        *,
        max_workers: int | None = None,
    ):
        if isinstance(calls, Mapping):
            keyed = dict(calls)
            return self._run_keyed_parallel(keyed, max_workers=max_workers)

        items = list(calls)
        if all(isinstance(item, tuple) and len(item) == 2 for item in items):
            keyed = {str(key): fn for key, fn in items}
            return self._run_keyed_parallel(keyed, max_workers=max_workers)

        funcs = [item for item in items if callable(item)]
        with ThreadPoolExecutor(max_workers=max_workers or len(funcs) or 1) as pool:
            futures = [pool.submit(fn) for fn in funcs]
            return [future.result() for future in futures]

    @staticmethod
    def _run_keyed_parallel(calls: dict[str, Callable[[], Any]], *, max_workers: int | None = None) -> dict[str, Any]:
        results: dict[str, Any] = {}
        with ThreadPoolExecutor(max_workers=max_workers or len(calls) or 1) as pool:
            futures: dict[Future, str] = {pool.submit(fn): key for key, fn in calls.items()}
            for future in as_completed(futures):
                results[futures[future]] = future.result()
        return results
