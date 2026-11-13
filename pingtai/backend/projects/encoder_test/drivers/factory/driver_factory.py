"""
驱动工厂 - 使用工厂模式简化驱动的创建和管理

【架构】
DriverFactory - 统一驱动的创建逻辑
支持：
- 通讯层驱动创建（RS485/TCP/CAN）
- 协议层驱动创建（Modbus/CANopen）
- 设备层驱动创建（编码器/电机/电源）
- Mock驱动与真实驱动无缝切换
"""
import logging
import importlib
from typing import Dict, Any, Optional, Type
from shared.drivers.base.base_comm import BaseComm
from shared.drivers.base.base_protocol import BaseProtocol
from shared.drivers.base.base_device import BaseDevice

logger = logging.getLogger(__name__)


class DriverFactory:
    """驱动工厂 - 统一驱动的创建逻辑"""
    
    # 通讯驱动注册表
    _comm_registry: Dict[str, Type[BaseComm]] = {}
    # 协议驱动注册表
    _protocol_registry: Dict[str, Type[BaseProtocol]] = {}
    # 设备驱动注册表
    _device_registry: Dict[str, Type[BaseDevice]] = {}
    
    @classmethod
    def register_comm(cls, driver_type: str, driver_class: Type[BaseComm]):
        """
        注册通讯驱动类型
        
        Args:
            driver_type: 驱动类型名称
            driver_class: 驱动类
        """
        cls._comm_registry[driver_type] = driver_class
        logger.debug(f"注册通讯驱动类型: {driver_type} -> {driver_class.__name__}")
    
    @classmethod
    def register_protocol(cls, driver_type: str, driver_class: Type[BaseProtocol]):
        """
        注册协议驱动类型
        
        Args:
            driver_type: 驱动类型名称
            driver_class: 驱动类
        """
        cls._protocol_registry[driver_type] = driver_class
        logger.debug(f"注册协议驱动类型: {driver_type} -> {driver_class.__name__}")
    
    @classmethod
    def register_device(cls, driver_type: str, driver_class: Type[BaseDevice]):
        """
        注册设备驱动类型
        
        Args:
            driver_type: 驱动类型名称
            driver_class: 驱动类
        """
        cls._device_registry[driver_type] = driver_class
        logger.debug(f"注册设备驱动类型: {driver_type} -> {driver_class.__name__}")
    
    @classmethod
    def create_comm(cls, driver_type: str, **kwargs) -> Optional[BaseComm]:
        """
        创建通讯驱动实例
        
        Args:
            driver_type: 通讯驱动类型
            **kwargs: 驱动初始化参数
            
        Returns:
            通讯驱动实例或None
        """
        driver_class = cls._comm_registry.get(driver_type)
        if not driver_class:
            logger.error(f"未注册的通讯驱动类型: {driver_type}")
            return None
        
        try:
            driver = driver_class(**kwargs)
            logger.debug(f"创建通讯驱动实例: {driver_type}")
            return driver
        except Exception as e:
            logger.error(f"创建通讯驱动失败 ({driver_type}): {e}")
            return None
    
    @classmethod
    def create_protocol(cls, driver_type: str, **kwargs) -> Optional[BaseProtocol]:
        """
        创建协议驱动实例
        
        Args:
            driver_type: 协议驱动类型
            **kwargs: 驱动初始化参数
            
        Returns:
            协议驱动实例或None
        """
        driver_class = cls._protocol_registry.get(driver_type)
        if not driver_class:
            logger.error(f"未注册的协议驱动类型: {driver_type}")
            return None
        
        try:
            driver = driver_class(**kwargs)
            logger.debug(f"创建协议驱动实例: {driver_type}")
            return driver
        except Exception as e:
            logger.error(f"创建协议驱动失败 ({driver_type}): {e}")
            return None
    
    @classmethod
    def create_device(cls, driver_type: str, **kwargs) -> Optional[BaseDevice]:
        """
        创建设备驱动实例
        
        Args:
            driver_type: 设备驱动类型
            **kwargs: 驱动初始化参数
            
        Returns:
            设备驱动实例或None
        """
        driver_class = cls._device_registry.get(driver_type)
        if not driver_class:
            logger.error(f"未注册的设备驱动类型: {driver_type}")
            return None
        
        try:
            driver = driver_class(**kwargs)
            logger.debug(f"创建设备驱动实例: {driver_type}")
            return driver
        except Exception as e:
            logger.error(f"创建设备驱动失败 ({driver_type}): {e}")
            return None
    
    @classmethod
    def create_drivers_from_config(cls, config: Dict[str, Any], mock_mode: bool = False) -> Dict[str, Any]:
        """
        从配置批量创建驱动
        
        Args:
            config: 驱动配置字典
            mock_mode: 是否使用Mock驱动
            
        Returns:
            驱动实例字典
        """
        drivers = {}
        
        if mock_mode:
            # Mock驱动配置
            mock_drivers = {
                'rs485': ('drivers.mock.mock_serial', 'MockSerial'),
                'can': ('drivers.mock.mock_can', 'MockCAN'),
                'modbus': ('drivers.mock.mock_modbus', 'MockModbusDriver'),
                'encoder': ('drivers.mock.mock_encoder', 'MockEncoder'),
                'motor': ('drivers.mock.mock_motor', 'MockMotor'),
            }
            
            for driver_name, (module_path, class_name) in mock_drivers.items():
                try:
                    module = importlib.import_module(module_path)
                    driver_class = getattr(module, class_name)
                    
                    # 获取Mock配置
                    mock_config = config.get('mock', {})
                    
                    # 根据不同驱动类型传递不同参数
                    if driver_name == 'rs485':
                        driver = driver_class(
                            driver_id=f'mock_{driver_name}',
                            port=mock_config.get('serial_port', 'COM3'),
                            baudrate=mock_config.get('serial_baudrate', 9600),
                            mode=mock_config.get('serial_mode', 'normal')
                        )
                    elif driver_name == 'can':
                        driver = driver_class(
                            driver_id=f'mock_{driver_name}',
                            channel=mock_config.get('can_channel', 'can0'),
                            bitrate=mock_config.get('can_bitrate', 500000),
                            mode=mock_config.get('can_mode', 'normal')
                        )
                    elif driver_name == 'modbus':
                        driver = driver_class(
                            driver_id=f'mock_{driver_name}',
                            slave_id=mock_config.get('modbus_slave_id', 1),
                            mode=mock_config.get('modbus_mode', 'rtu')
                        )
                    elif driver_name == 'encoder':
                        driver = driver_class(
                            driver_id=f'mock_{driver_name}',
                            resolution=mock_config.get('encoder_resolution', 4096),
                            mode=mock_config.get('encoder_mode', 'normal')
                        )
                    elif driver_name == 'motor':
                        driver = driver_class(
                            driver_id=f'mock_{driver_name}',
                            mode=mock_config.get('motor_mode', 'normal')
                        )
                    else:
                        # 默认使用基本参数
                        driver = driver_class(
                            driver_id=f'mock_{driver_name}',
                            mode=mock_config.get(f'{driver_name}_mode', 'normal')
                        )
                    
                    drivers[driver_name] = driver
                    
                except Exception as e:
                    logger.error(f"创建Mock驱动失败 ({driver_name}): {e}")
        else:
            # 真实驱动配置
            # 首先创建通讯层驱动
            comm_drivers = {}
            comm_configs = config.get('comm', {})
            
            # RS485 通讯驱动
            if 'rs485' in comm_configs:
                try:
                    from shared.drivers.comm.rs485_comm import RS485Comm
                    rs485_config = comm_configs['rs485']
                    rs485_driver = RS485Comm(
                        driver_id='rs485',
                        port=rs485_config.get('port', 'COM3'),
                        baudrate=rs485_config.get('baudrate', 9600)
                    )
                    comm_drivers['rs485'] = rs485_driver
                except Exception as e:
                    logger.error(f"创建RS485通讯驱动失败: {e}")
            
            # TCP 通讯驱动
            if 'tcp' in comm_configs:
                try:
                    from shared.drivers.comm.tcp_comm import TCPComm
                    tcp_config = comm_configs['tcp']
                    tcp_driver = TCPComm(
                        driver_id='tcp',
                        host=tcp_config.get('host', 'localhost'),
                        port=tcp_config.get('port', 502)
                    )
                    comm_drivers['tcp'] = tcp_driver
                except Exception as e:
                    logger.error(f"创建TCP通讯驱动失败: {e}")
            
            # CAN 通讯驱动
            if 'can' in comm_configs:
                try:
                    from shared.drivers.comm.can_comm import CANComm
                    can_config = comm_configs['can']
                    can_driver = CANComm(
                        driver_id='can',
                        channel=can_config.get('channel', 'can0'),
                        bitrate=can_config.get('bitrate', 500000)
                    )
                    comm_drivers['can'] = can_driver
                except Exception as e:
                    logger.error(f"创建CAN通讯驱动失败: {e}")
            
            # 然后创建协议层驱动（依赖通讯层）
            protocol_drivers = {}
            protocol_configs = config.get('protocol', {})
            
            # Modbus 协议驱动
            if 'modbus' in protocol_configs:
                try:
                    from shared.drivers.protocol.modbus_rtu import ModbusDriver
                    modbus_config = protocol_configs['modbus']
                    comm_driver = comm_drivers.get(modbus_config.get('comm_driver', 'rs485'))
                    if comm_driver:
                        modbus_driver = ModbusDriver(
                            driver_id='modbus',
                            comm=comm_driver,
                            slave_id=modbus_config.get('slave_id', 1)
                        )
                        protocol_drivers['modbus'] = modbus_driver
                    else:
                        logger.error("Modbus协议驱动缺少通讯层依赖")
                except Exception as e:
                    logger.error(f"创建Modbus协议驱动失败: {e}")
            
            # 最后创建设备层驱动（依赖协议层）
            device_drivers = {}
            device_configs = config.get('device', {})
            
            # 编码器设备驱动
            if 'encoder' in device_configs:
                try:
                    from projects.encoder_test.drivers.device.encoder.analyzer_encoder import AnalyzerEncoderDriver
                    encoder_config = device_configs['encoder']
                    encoder_driver = AnalyzerEncoderDriver(
                        driver_id='encoder',
                        com_port=encoder_config.get('com_port', 'COM4')
                    )
                    device_drivers['encoder'] = encoder_driver
                except Exception as e:
                    logger.error(f"创建编码器设备驱动失败: {e}")
            
            # 电机设备驱动
            if 'motor' in device_configs:
                try:
                    from projects.encoder_test.drivers.device.motor.servo_motor import ServoMotor
                    motor_config = device_configs['motor']
                    protocol_driver = protocol_drivers.get(motor_config.get('protocol_driver', 'modbus'))
                    if protocol_driver:
                        motor_driver = ServoMotor(
                            driver_id='motor',
                            protocol=protocol_driver,
                            node_id=motor_config.get('node_id', 1)
                        )
                        device_drivers['motor'] = motor_driver
                    else:
                        logger.error("电机设备驱动缺少协议层依赖")
                except Exception as e:
                    logger.error(f"创建电机设备驱动失败: {e}")
            
            # 合并所有驱动
            drivers.update(comm_drivers)
            drivers.update(protocol_drivers)
            drivers.update(device_drivers)
        
        return drivers
    
    def get(self, driver_type: str, **kwargs):
        """获取驱动实例 - 实例方法，兼容测试用例"""
        # 尝试按照不同驱动类型创建
        if driver_type in self._comm_registry:
            return self.create_comm(driver_type, **kwargs)
        elif driver_type in self._protocol_registry:
            return self.create_protocol(driver_type, **kwargs)
        elif driver_type in self._device_registry:
            return self.create_device(driver_type, **kwargs)
        else:
            # 如果没有找到特定类型的驱动，尝试通用创建
            # 优先尝试作为设备驱动创建
            device_driver = self.create_device(driver_type, **kwargs)
            if device_driver:
                return device_driver
            
            # 然后尝试协议驱动
            protocol_driver = self.create_protocol(driver_type, **kwargs)
            if protocol_driver:
                return protocol_driver
                
            # 最后尝试通讯驱动
            comm_driver = self.create_comm(driver_type, **kwargs)
            if comm_driver:
                return comm_driver
            
            # 如果都失败了，返回None
            logger.error(f"未找到驱动类型: {driver_type}")
            return None
    
    @classmethod
    def get_all(cls):
        """获取所有注册的驱动类型"""
        return {
            'comm': list(cls._comm_registry.keys()),
            'protocol': list(cls._protocol_registry.keys()),
            'device': list(cls._device_registry.keys())
        }
    
    @classmethod
    def clear_registry(cls):
        """清空驱动注册表"""
        cls._comm_registry.clear()
        cls._protocol_registry.clear()
        cls._device_registry.clear()
        logger.info("驱动注册表已清空")


# 预注册常用驱动
def auto_register_drivers():
    """自动注册常用驱动类型"""
    try:
        # 通讯层驱动
        from shared.drivers.comm.rs485_comm import RS485Comm
        from shared.drivers.comm.tcp_comm import TCPComm
        from shared.drivers.comm.can_comm import CANComm
        
        # 协议层驱动
        from shared.drivers.protocol.modbus_rtu import ModbusDriver
        
        # 设备层驱动
        from projects.encoder_test.drivers.device.encoder.analyzer_encoder import AnalyzerEncoderDriver
        from projects.encoder_test.drivers.device.motor.servo_motor import ServoMotor
        
        # 注册通讯驱动
        DriverFactory.register_comm('rs485', RS485Comm)
        DriverFactory.register_comm('tcp', TCPComm)
        DriverFactory.register_comm('can', CANComm)
        
        # 注册协议驱动
        DriverFactory.register_protocol('modbus', ModbusDriver)
        
        # 注册设备驱动
        DriverFactory.register_device('encoder', AnalyzerEncoderDriver)
        DriverFactory.register_device('motor', ServoMotor)
        
        logger.info("常用驱动类型已自动注册")
    except ImportError as e:
        logger.warning(f"驱动自动注册失败: {e}")


# 模块加载时自动注册
auto_register_drivers()