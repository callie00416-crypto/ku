"""
pytest 配置文件 - 共享 Fixtures

【真实设备测试配置】
- 功率放大器 ATA-101B: USB串口
- 波形发生器 RIGOL DG811: USBTMC
- 编码器 KingKong Analyzer: USB串口
- ASDB2电机驱动器: RS485 MODBUS-RTU
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest


@pytest.fixture(scope="session")
def asdb2_driver():
    """ASDB2驱动器Fixture - Session级别
    
    整个测试会话只创建一次
    """
    from shared.drivers.comm.rs485_comm import RS485Comm
    from shared.drivers.protocol.modbus_rtu import ModbusDriver
    from projects.encoder_test.drivers.device.ASDB2.asdb2_driver import ASDB2Driver
    
    print("\n创建ASDB2驱动器...")
    
    # 创建通讯层
    comm = RS485Comm(
        driver_id='rs485_asdb2',
        port='COM4',
        baudrate=38400,
        parity='N',
        stopbits=2,
        bytesize=8,
        timeout=2.0
    )
    
    # 创建协议层
    protocol = ModbusDriver(
        driver_id='modbus_asdb2',
        comm=comm,
        slave_id=0x7F,
        mode='rtu'
    )
    
    # 创建设备驱动
    driver = ASDB2Driver(
        driver_id='asdb2',
        protocol=protocol,
        slave_id=0x7F
    )
    
    # 连接设备
    assert driver.connect(), "连接ASDB2失败"
    
    # 初始化驱动器
    assert driver.initialize_driver(), "初始化ASDB2失败"
    
    yield driver
    
    # 清理
    print("\n清理ASDB2驱动器...")
    try:
        driver.stop_motor()
        driver.enable_servo(False)
        driver.disconnect()
    except Exception as e:
        print(f"清理ASDB2失败: {e}")


@pytest.fixture
def motor(asdb2_driver):
    """MotorAction Fixture - Function级别
    
    每个测试函数都会创建新的MotorAction
    """
    from projects.encoder_test.actions.motor_action import MotorAction
    
    motor = MotorAction(asdb2_driver)
    yield motor
    # 清理：停止电机
    try:
        motor.stop()
    except Exception as e:
        print(f"停止电机失败: {e}")


@pytest.fixture
def encoder():
    """编码器设备 Fixture - 使用真实设备"""
    from projects.encoder_test.drivers.device.encoder.analyzer_encoder import AnalyzerEncoderDriver
    # 直接指定串口端口，绕过 Analyzer.list() 问题
    enc = AnalyzerEncoderDriver(driver_id='enc1', com_port='COM4')
    enc.connect()
    return enc


@pytest.fixture
def power_amplifier():
    """功率放大器设备 Fixture - 使用真实设备"""
    from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier
    
    # 先扫描可用串口
    import serial.tools.list_ports
    ports = [port.device for port in serial.tools.list_ports.comports()]
    
    # 排除编码器占用的 COM4，尝试其他串口
    available_ports = [p for p in ports if p != 'COM4']
    
    # 创建协议层（USB串口）- 使用 RS485Comm 作为串口通讯
    from shared.drivers.comm.rs485_comm import RS485Comm
    from shared.drivers.protocol.custom_ascii_protocol import CustomASCIIProtocol
    
    # 优先使用 COM3，如果不可用则尝试其他串口
    port = 'COM3' if 'COM3' in available_ports else (available_ports[0] if available_ports else 'COM1')
    
    comm = RS485Comm(driver_id='pa_comm', port=port, baudrate=9600)
    # 设备层已经处理命令前缀后缀，协议层保持为空
    protocol = CustomASCIIProtocol(driver_id='pa_protocol', comm=comm, 
                                  command_prefix='', command_suffix='')
    
    pa = ATA101BPowerAmplifier(driver_id='pa1', protocol=protocol)
    pa.connect()
    return pa


@pytest.fixture
def waveform_generator():
    """波形发生器设备 Fixture - 使用真实设备"""
    from projects.encoder_test.drivers.device.waveform_generator.dg811 import DG811WaveformGenerator
    
    # 使用 pyvisa 连接波形发生器
    import pyvisa
    import time
    
    # 创建VISA通信类
    class VisaComm:
        def __init__(self, instrument):
            self.instrument = instrument
            self._is_open = True
        
        def send(self, data):
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            self.instrument.write(data)
            time.sleep(0.05)
            return len(data)
        
        def recv(self, size=1024, timeout=1.0):
            try:
                data = self.instrument.read()
                if isinstance(data, str):
                    data = data.encode('utf-8')
                return data
            except:
                return None
        
        @property
        def is_open(self):
            return self._is_open
        
        def close(self):
            self.instrument.close()
            self._is_open = False
    
    from shared.drivers.protocol.scpi_protocol import SCPIProtocol
    
    # 扫描并连接波形发生器
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    
    # 查找波形发生器设备（RIGOL DG811）
    resource_string = None
    for res in resources:
        if '0x1AB1' in res and '0x0643' in res:  # RIGOL DG811 的 VID/PID
            resource_string = res
            break
    
    if resource_string:
        instrument = rm.open_resource(resource_string)
        instrument.timeout = 10000
        
        comm = VisaComm(instrument)
        protocol = SCPIProtocol(driver_id='wg_protocol', comm=comm)
        protocol.connect()
        
        wg = DG811WaveformGenerator(driver_id='wg1', protocol=protocol)
        wg.connect()
        return wg
    else:
        return None


@pytest.fixture
def devices(encoder, power_amplifier, waveform_generator):
    """设备集合 Fixture"""
    return {
        'encoder': encoder,
        'power_amplifier': power_amplifier,
        'waveform_generator': waveform_generator,
    }


def pytest_configure(config):
    """注册自定义 markers"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "driver: 驱动层测试")
    config.addinivalue_line("markers", "action: 动作层测试")
    config.addinivalue_line("markers", "flow: 流程层测试")
    config.addinivalue_line("markers", "case: 用例层测试")
    config.addinivalue_line("markers", "integration_real: 真实设备集成测试")
    config.addinivalue_line("markers", "asdb2: ASDB2电机驱动器测试")