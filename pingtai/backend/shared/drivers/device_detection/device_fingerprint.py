"""设备指纹库

定义各种工业设备的识别特征
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DeviceFingerprint:
    """设备指纹"""
    device_type: str
    name: str
    vid: Optional[str] = None
    pid: Optional[str] = None
    serial_number: Optional[str] = None
    description_pattern: Optional[str] = None
    protocol: str = 'unknown'
    baud_rate: int = 9600
    test_command: Optional[Any] = None
    expected_response: Optional[Any] = None
    response_timeout: float = 0.5
    retry_count: int = 3


DEVICE_FINGERPRINTS: Dict[str, DeviceFingerprint] = {
    'asdb2_motor': DeviceFingerprint(
        device_type='asdb2_motor',
        name='ASDB2电机驱动器',
        vid='10C4',
        pid='EA60',
        serial_number='0001',
        description_pattern='CP210x',
        protocol='modbus_rtu',
        baud_rate=115200,
        test_command=[0x7F, 0x03, 0x00, 0x00, 0x00, 0x01],
        expected_response=[0x7F, 0x03, 0x02],
        response_timeout=0.5,
        retry_count=3
    ),
    
    'dpt_encoder': DeviceFingerprint(
        device_type='dpt_encoder',
        name='DPT磁双编码器',
        vid='6B6B',
        pid='0001',
        serial_number='20260123154427',
        description_pattern='USB',
        protocol='analyzer',
        baud_rate=2500000,
        test_command=0x33,
        expected_response=7,
        response_timeout=0.2,
        retry_count=3
    ),
    
    'ata101b_power_amplifier': DeviceFingerprint(
        device_type='ata101b_power_amplifier',
        name='ATA-101B功率放大器',
        vid='0403',
        pid='6001',
        serial_number='BG0248H7A',
        description_pattern='FTDI',
        protocol='custom_ascii',
        baud_rate=115200,
        test_command='ATA,SET,OUTP?',
        expected_response='OK',
        response_timeout=0.5,
        retry_count=3
    ),
    
    'dg811_waveform_generator': DeviceFingerprint(
        device_type='dg811_waveform_generator',
        name='RIGOL DG811波形发生器',
        vid='C0F4',  # 实际发现的VID
        pid='07C0',  # 实际发现的PID
        description_pattern='USB Composite Device',
        protocol='usbtmc',
        baud_rate=0,
        test_command=None,
        expected_response='RIGOL',
        response_timeout=0.5,
        retry_count=3
    ),
    
    'generic_modbus': DeviceFingerprint(
        device_type='generic_modbus',
        name='通用Modbus设备',
        vid=None,
        pid=None,
        description_pattern=None,
        protocol='modbus_rtu',
        baud_rate=9600,
        test_command=[0x01, 0x03, 0x00, 0x00, 0x00, 0x01],
        expected_response=[0x01, 0x03, 0x02],
        response_timeout=0.5,
        retry_count=3
    ),
    
    'unknown': DeviceFingerprint(
        device_type='unknown',
        name='未知设备',
        vid=None,
        pid=None,
        description_pattern=None,
        protocol='unknown',
        baud_rate=9600,
        test_command=None,
        expected_response=None
    )
}


def get_fingerprint(device_type: str) -> Optional[DeviceFingerprint]:
    """获取设备指纹"""
    return DEVICE_FINGERPRINTS.get(device_type)


def get_all_fingerprints() -> Dict[str, DeviceFingerprint]:
    """获取所有设备指纹"""
    return DEVICE_FINGERPRINTS.copy()


def match_fingerprint_by_hwid(hwid: str) -> Optional[DeviceFingerprint]:
    """通过硬件ID匹配设备指纹"""
    for fp in DEVICE_FINGERPRINTS.values():
        if fp.vid and fp.vid in hwid:
            if fp.pid and fp.pid in hwid:
                return fp
    return None


def match_fingerprint_by_description(description: str) -> List[DeviceFingerprint]:
    """通过描述匹配设备指纹"""
    matches = []
    for fp in DEVICE_FINGERPRINTS.values():
        if fp.description_pattern and fp.description_pattern.lower() in description.lower():
            matches.append(fp)
    return matches