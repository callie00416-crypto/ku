from __future__ import annotations

from driver_control import ControlSystem
import time


config = {
    "analyzers": [
        {"id": "a1", "port": "COM7"}
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


def main() -> None:
    with ControlSystem.from_config(config) as system:
        # print(system.devices["servo_1"].__dict__)
        # # {'id': 'servo_1', 'analyzer': <...>, 'protocol': <driver_control.protocols.RS485.Servo.Rs485ServoProtocol object at ...>, 'config': {'id': 'servo_1', 'kind': 'servo', 'protocol': 'rs485-servo', ...}}
        # print(system.analyzers["a1"].__dict__)
        # # {'port': 'COM7', 'serial_number': None, 'serial_baud': 115200, 'read_timeout': 0.001, '_serial_factory': None, '_serial': Serial<id=0x21d697ab550, open=True>(port='COM7', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.001, xonxoff=False, rtscts=False, dsrdtr=False), '_packets': <queue.Queue object at 0x0000021D697A9490>, '_transaction_lock': <unlocked _thread.RLock object owner=0 count=0 at 0x0000021D697BD0C0>, '_request_lock': <unlocked _thread.lock object at 0x0000021D697BE740>, '_request_id': 0, '_stop_event': <threading.Event at 0x21d697ab200: unset>, '_reader': <Thread(AnalyzerReader-COM7, started daemon 23532)>, '_last_error': None}
        servo = system.devices["servo_1"]
        analyzer1 = system.analyzers["a1"]
        analyzer1.enter_rs485_direct_mode(baud_rate=2_500_000)
        time.sleep(0.5)
        # servo.write_register(0x30, 2, transport="passthrough")
        # servo.write_register(0x35, 200, transport="passthrough")
        # servo.write_register(0xf0, 255, transport="passthrough")
        # print("Status via passthrough:", servo.read_register(0x60, count=3, transport="passthrough"))
        print(servo.read(register=0x60, count=3, transport="passthrough"))

        system.analyzers["a1"].enter_normal_mode()
        time.sleep(0.5)
        servo.write_register(0xf0, 0, transport="single-read")
        print("Status via passthrough:", servo.read_register(0x60, count=3, transport="single-read"))

if __name__ == "__main__":
    main()
