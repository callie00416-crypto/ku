from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TYPE_ALIASES = {
    "B": "uint8",
    "b": "int8",
    "H": "uint16",
    "h": "int16",
    "I": "uint32",
    "i": "int32",
    "f": "float32",
    "T": "uint24",
}


@dataclass(frozen=True)
class RegisterDefinition:
    address: int
    type: str
    name: str
    access_mode: str = "RW"


RAW_REGISTERS: dict[int, dict[str, Any]] = {
    0x01: {"type": "B", "name": "BusID"},
    0x02: {"type": "I", "name": "Baudrate"},
    0x03: {"type": "T", "name": "ZeroPositionInner"},
    0x04: {"type": "T", "name": "ZeroPositionOuter"},
    0x11: {"type": "f", "name": "Current Proportion"},
    0x12: {"type": "f", "name": "Current Integral"},
    0x13: {"type": "f", "name": "Current Derivative"},
    0x14: {"type": "f", "name": "Current FeedForward"},
    0x15: {"type": "f", "name": "Current Out Limit Abs"},
    0x16: {"type": "f", "name": "Velocity Proportion"},
    0x17: {"type": "f", "name": "Velocity Integral"},
    0x18: {"type": "f", "name": "Velocity Derivative"},
    0x19: {"type": "f", "name": "Velocity FeedForward"},
    0x1A: {"type": "f", "name": "Velocity Out Limit Abs"},
    0x1B: {"type": "f", "name": "Pos Proportion"},
    0x1C: {"type": "f", "name": "Pos Integral"},
    0x1D: {"type": "f", "name": "Pos Derivative"},
    0x1E: {"type": "f", "name": "Pos FeedForward"},
    0x1F: {"type": "f", "name": "Pos Out Limit Abs"},
    0x20: {"type": "I", "name": "ProductId"},
    0x21: {"type": "I", "name": "VersionData"},
    0x22: {"type": "I", "name": "McuGuid1"},
    0x23: {"type": "I", "name": "McuGuid2"},
    0x24: {"type": "I", "name": "McuGuid3"},
    0x30: {"type": "B", "name": "Motor Mode"},
    0x31: {"type": "f", "name": "Accel"},
    0x32: {"type": "f", "name": "Decel"},
    0x33: {"type": "f", "name": "Muti Pos Limit L Abs"},
    0x34: {"type": "f", "name": "Muti Pos Limit H Abs"},
    0x35: {"type": "f", "name": "Target Velocity"},
    0x36: {"type": "f", "name": "Target Position"},
    0x37: {"type": "f", "name": "Target Q Current"},
    0x38: {"type": "f", "name": "TargetTorqueSensless"},
    0x39: {"type": "f", "name": "Over Current Point"},
    0x3A: {"type": "H", "name": "Over Current Time"},
    0x3B: {"type": "f", "name": "Shut Current Point"},
    0x3C: {"type": "H", "name": "Shut Current Time"},
    0x3D: {"type": "B", "name": "Pcb Temp Limit"},
    0x3E: {"type": "B", "name": "Fpc Temp Limit"},
    0x3F: {"type": "f", "name": "Over Voltage Point"},
    0x40: {"type": "f", "name": "Low Voltage Point"},
    0x41: {"type": "f", "name": "GearRate"},
    0x42: {"type": "I", "name": "Polarity"},
    0x43: {"type": "f", "name": "Torque_pos_kp"},
    0x44: {"type": "f", "name": "Torque_pos_kd"},
    0x45: {"type": "f", "name": "Torque_pos_Tau"},
    0x46: {"type": "I", "name": "LedEnable"},
    0x47: {"type": "f", "name": "Current_Q_Max_Set"},
    0x48: {"type": "f", "name": "TorquePos_OutLimit"},
    0x49: {"type": "B", "name": "FOC_Enable"},
    0x4A: {"type": "B", "name": "Debugger", "accessMode": "W"},
    0x60: {"type": "B", "name": "Status Flags"},
    0x61: {"type": "f", "name": "CurrentA Actual"},
    0x62: {"type": "f", "name": "CurrentB Actual"},
    0x63: {"type": "f", "name": "CurrentC Actual"},
    0x64: {"type": "f", "name": "Velocity Actual"},
    0x65: {"type": "f", "name": "Position Actual"},
    0x66: {"type": "f", "name": "Duty Actual"},
    0x67: {"type": "f", "name": "Bus Voltage"},
    0x68: {"type": "f", "name": "CurrentQ Actual"},
    0x69: {"type": "I", "name": "Inner Angle"},
    0x6A: {"type": "I", "name": "Outer Angle"},
    0x6B: {"type": "b", "name": "Pcba Temperature"},
    0x6C: {"type": "b", "name": "Fpc Temperature"},
    0x6D: {"type": "f", "name": "Torque Actual"},
    0x6E: {"type": "f", "name": "Position Inner Actual"},
    0x6F: {"type": "f", "name": "CurrentD Actual"},
    0x80: {"type": "B", "name": "Recalibration", "accessMode": "W"},
    0xE0: {"type": "I", "name": "SystemRst", "accessMode": "W"},
    0xE1: {"type": "I", "name": "SystemSleep", "accessMode": "W"},
    0xF0: {"type": "B", "name": "Control Run", "accessMode": "W"},
    0xF1: {"type": "B", "name": "Save Parameters", "accessMode": "W"},
    0xF2: {"type": "B", "name": "Command Mode", "accessMode": "W"},
}


REGISTERS = {
    addr: RegisterDefinition(
        address=addr,
        type=TYPE_ALIASES.get(str(cfg["type"]), str(cfg["type"])),
        name=str(cfg["name"]),
        access_mode=str(cfg.get("accessMode", "RW")),
    )
    for addr, cfg in RAW_REGISTERS.items()
}
