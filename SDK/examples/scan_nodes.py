from __future__ import annotations

from driver_control import ControlSystem
import time




def main() -> None:
    print("Analyzers:", ControlSystem.scan_analyzers())
    config = {
        "analyzers": [{"id": "a1", "port": "COM7"},{"id": "a2", "port": "COM8"}],
        "devices": [{"id": "scanner1", "kind": "servo", "protocol": "rs485-servo", "analyzer": "a1"},{"id": "scanner2", "kind": "servo", "protocol": "rs485-servo", "analyzer": "a2"}],
    }
    with ControlSystem.from_config(config) as system:
        nodes1 = system.scan_nodes("scanner1", start=0, end=30)
        nodes2 = system.scan_nodes("scanner2", start=0, end=30)
        print("Found nodes:", nodes1, nodes2)
        scanner1 = system.devices["scanner1"]
        scanner2 = system.devices["scanner2"]
        for node in nodes1:
            print(node, scanner1.read_mcu_guid(node))
        for node in nodes2:
            print(node, scanner2.read_mcu_guid(node))

if __name__ == "__main__":
    main()
