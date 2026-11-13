from __future__ import annotations

import time
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


# def main() -> None:
#     with ControlSystem.from_config(config) as system:
#         t0 = time.perf_counter()

#         def timed(name, fn):
#             def wrapper():
#                 t_start = time.perf_counter()
#                 print(f"{name} start at {t_start - t0:.6f}s")
#                 result = fn()
#                 t_end = time.perf_counter()
#                 print(f"{name} end   at {t_end - t0:.6f}s")
#                 return result

#             return wrapper

#         results = system.run_parallel(
#             {
#                 "servo_1_pos": timed(
#                     "servo_1",
#                     lambda: system.devices["servo_1"].read_register(0x60),
#                 ),
#                 "servo_2_pos": timed(
#                     "servo_2",
#                     lambda: system.devices["servo_2"].read_register(0x60),
#                 ),
#             }
#         )

#         t1 = time.perf_counter()
#         print("results:", results)
#         print(f"total elapsed: {t1 - t0:.6f}s")

def main() -> None:
    with ControlSystem.from_config(config) as system:
        t0 = time.perf_counter()

        def timed(name, fn):
            def wrapper():
                t_start = time.perf_counter()
                print(f"{name} start at {t_start - t0:.6f}s")
                result = fn()
                t_end = time.perf_counter()
                print(f"{name} end   at {t_end - t0:.6f}s")
                return result

            return wrapper

        for i in range(5):
            print(f"\n=== round {i} ===")
            round_start = time.perf_counter()
            results = system.run_parallel(
                {
                    "servo_1_pos": timed(
                        f"round{i}-servo_1",
                        lambda: system.devices["servo_1"].read_register(0x60),
                    ),
                    "servo_2_pos": timed(
                        f"round{i}-servo_2",
                        lambda: system.devices["servo_2"].read_register(0x60),
                    ),
                }
            )
            round_end = time.perf_counter()
            print("results:", results)
            print(f"round {i} elapsed: {round_end - round_start:.6f}s")

        total_end = time.perf_counter()
        print(f"\nall rounds total elapsed: {total_end - t0:.6f}s")


if __name__ == "__main__":
    main()