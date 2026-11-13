from __future__ import annotations

from driver_control import ControlSystem


config = {
    "analyzers": [
        {"id": "a1", "port": "COM7"},
        {"id": "a2", "port": "COM8"},
    ],
    "devices": [
        {"id": "servo_1", "kind": "servo", "protocol": "rs485-servo", "analyzer": "a1", "node_id": 10},
        {"id": "servo_2", "kind": "servo", "protocol": "rs485-servo", "analyzer": "a2", "node_id": 14},
    ],
}


def main() -> None:
    with ControlSystem.from_config(config) as system:
        results = system.run_parallel(
            {
                "servo_1_pos": lambda: system.devices["servo_1"].read_register(0x60),
                "servo_2_pos": lambda: system.devices["servo_2"].read_register(0x60),
            }
        )
        print(results)


if __name__ == "__main__":
    main()
