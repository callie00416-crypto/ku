from __future__ import annotations

from driver_control import ControlSystem
import time
import statistics


CONFIG = {
    "analyzers": [
        {"id": "a1", "port": "COM7"},
    ],
    "devices": [
        {
            "id": "servo_1",
            "kind": "servo",
            "protocol": "rs485-servo",
            "analyzer": "a1",
            "node_id": 10,
            "rs485_baud": 2_500_000,
        }
    ],
}


def benchmark_read(servo, mode: str, duration_s: float = 10.0):
    print(f"\n===== Benchmark mode: {mode} =====")

    intervals = []
    values = []

    start = time.perf_counter()
    last = start

    count = 0

    while True:
        now = time.perf_counter()
        if now - start >= duration_s:
            break

        t0 = now

        try:
            val = servo.read_register(0x60, count=3, transport=mode)
        except Exception as e:
            print("Read error:", e)
            continue

        t1 = time.perf_counter()

        dt = t1 - last
        last = t1

        intervals.append(dt)
        values.append(val)
        count += 1

    total_time = time.perf_counter() - start

    if not intervals:
        print("No valid reads.")
        return

    hz = count / total_time

    print(f"Total reads: {count}")
    print(f"Total time: {total_time:.4f} s")
    print(f"Average Hz: {hz:.2f}")

    print(f"Min interval: {min(intervals)*1000:.3f} ms")
    print(f"Max interval: {max(intervals)*1000:.3f} ms")
    print(f"Avg interval: {statistics.mean(intervals)*1000:.3f} ms")


def main():
    with ControlSystem.from_config(CONFIG) as system:
        servo = system.devices["servo_1"]

        # ===== passthrough =====
        system.analyzers["a1"].enter_rs485_direct_mode(baud_rate=2_500_000)
        time.sleep(1)

        benchmark_read(servo, mode="passthrough", duration_s=1)

        # ===== single-read =====
        system.analyzers["a1"].enter_normal_mode()
        time.sleep(1)

        benchmark_read(servo, mode="single-read", duration_s=1)


if __name__ == "__main__":
    main()