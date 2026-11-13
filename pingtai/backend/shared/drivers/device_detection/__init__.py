"""设备检测模块

提供自动发现和识别串口设备的能力
"""
from .device_fingerprint import (
    DeviceFingerprint,
    get_fingerprint,
    get_all_fingerprints,
    match_fingerprint_by_hwid,
    match_fingerprint_by_description,
    DEVICE_FINGERPRINTS
)

from .serial_detector import (
    SerialDeviceDetector,
    SerialPortInfo,
    DeviceInfo
)

__all__ = [
    'DeviceFingerprint',
    'get_fingerprint',
    'get_all_fingerprints',
    'match_fingerprint_by_hwid',
    'match_fingerprint_by_description',
    'DEVICE_FINGERPRINTS',
    'SerialDeviceDetector',
    'SerialPortInfo',
    'DeviceInfo'
]