"""
Modbus 协议驱动 - 协议层实现

【架构】
ModbusDriver(BaseProtocol)  - 使用 RS485Comm 进行通讯

【组合关系】
Device -> ModbusDriver -> RS485Comm
"""
import logging
from typing import Optional, Dict, Any
from ..base.base_protocol import BaseProtocol

logger = logging.getLogger(__name__)


class ModbusDriver(BaseProtocol):
    """Modbus 协议驱动 - 使用组合持有通讯层"""
    
    def __init__(self, driver_id: str = 'modbus', comm: BaseProtocol = None,
                 slave_id: int = 1, mode: str = 'rtu', **kwargs):
        super().__init__(driver_id, comm, **kwargs)
        self.slave_id = slave_id
        self.mode = mode
        self._client = None
        self._modbus_factory = kwargs.get('modbus_factory', None)
        
        if self._modbus_factory is None:
            try:
                from pymodbus.client import ModbusSerialClient, ModbusTcpClient
                self._modbus_factory = {
                    'serial': ModbusSerialClient,
                    'tcp': ModbusTcpClient
                }
            except ImportError:
                logger.warning("pymodbus 未安装")

    def connect(self) -> bool:
        """连接设备"""
        if not self.comm:
            logger.error("Modbus 缺少通讯层")
            return False
        
        try:
            if self.mode == 'rtu':
                # 获取串口参数
                port = getattr(self.comm, 'port', 'COM1')
                baudrate = getattr(self.comm, 'baudrate', 9600)
                timeout = getattr(self.comm, 'timeout', 1.0)
                parity = getattr(self.comm, 'parity', 'N')
                stopbits = getattr(self.comm, 'stopbits', 1)
                bytesize = getattr(self.comm, 'bytesize', 8)
                
                # 创建pymodbus客户端
                if 'serial' in self._modbus_factory:
                    self._client = self._modbus_factory['serial'](
                        port=port,
                        baudrate=baudrate,
                        timeout=timeout,
                        parity=parity,
                        stopbits=stopbits,
                        bytesize=bytesize
                    )
                    
                    # 连接客户端
                    if self._client.connect():
                        self._is_connected = True
                        self.reset_error()
                        logger.info(f"Modbus 连接成功: {self.mode.upper()}")
                        return True
                    else:
                        logger.error("Modbus 客户端连接失败")
                        return False
                else:
                    logger.error("Modbus serial 工厂不可用")
                    return False
            else:
                self._is_connected = True
                self.reset_error()
                return True
                
        except Exception as e:
            logger.error(f"Modbus 连接失败: {e}")
            self._is_connected = False
            self.increment_error()
            return False

    def disconnect(self):
        """断开连接"""
        if self._client:
            try:
                if hasattr(self._client, 'close'):
                    self._client.close()
            except Exception as e:
                logger.error(f"Modbus 关闭失败: {e}")
        self._client = None
        self._is_connected = False
        logger.info(f"Modbus 已断开: {self.driver_id}")

    def is_connected(self) -> bool:
        """检查连接状态"""
        if not self._client:
            return False
        if hasattr(self._client, 'is_socket_open'):
            return self._client.is_socket_open()
        if hasattr(self._client, 'connected'):
            return self._client.connected
        return self._is_connected

    def reconnect(self) -> bool:
        """重新连接设备（用于连接断开后恢复）"""
        logger.info("Modbus 重新连接...")
        if self._client:
            try:
                if hasattr(self._client, 'close'):
                    self._client.close()
            except Exception as e:
                logger.warning(f"Modbus 关闭旧连接失败: {e}")
        self._client = None
        self._is_connected = False
        return self.connect()

    def _ensure_connected(self) -> bool:
        """确保连接有效，如果连接断开则自动重连"""
        if self.is_connected():
            return True
        logger.warning("Modbus 连接已断开，尝试自动重连...")
        return self.reconnect()

    def read_register(self, address: int, slave_id: int = None) -> Optional[int]:
        """读单个寄存器"""
        if not self._ensure_connected():
            raise ConnectionError("Modbus 未连接且重连失败")
        try:
            sid = slave_id or self.slave_id
            result = self._client.read_holding_registers(address, count=1, device_id=sid)
            if result and not result.isError():
                self.reset_error()
                return result.registers[0]
            logger.error(f"读寄存器失败: {result}")
            self.increment_error()
            return None
        except Exception as e:
            logger.error(f"读寄存器异常: {e}")
            self.increment_error()
            return None

    def read_registers(self, address: int, count: int = 1, slave_id: int = None) -> Optional[list]:
        """读多个寄存器"""
        if not self._ensure_connected():
            raise ConnectionError("Modbus 未连接且重连失败")
        try:
            sid = slave_id or self.slave_id
            result = self._client.read_holding_registers(address, count=count, device_id=sid)
            if result and not result.isError():
                self.reset_error()
                return result.registers[:count]
            logger.error(f"读多个寄存器失败: {result}")
            self.increment_error()
            return None
        except Exception as e:
            logger.error(f"读多个寄存器异常: {e}")
            self.increment_error()
            return None

    def write_register(self, address: int, value: int, slave_id: int = None) -> bool:
        """写单个寄存器"""
        if not self._ensure_connected():
            raise ConnectionError("Modbus 未连接且重连失败")
        try:
            sid = slave_id or self.slave_id
            result = self._client.write_register(address, value, device_id=sid)
            if result and not result.isError():
                self.reset_error()
                return True
            logger.error(f"写寄存器失败: {result}")
            self.increment_error()
            return False
        except Exception as e:
            logger.error(f"写寄存器异常: {e}")
            self.increment_error()
            return False

    def read_long(self, address: int, slave_id: int = None) -> Optional[int]:
        """读 32 位数据"""
        if not self._ensure_connected():
            raise ConnectionError("Modbus 未连接且重连失败")
        try:
            sid = slave_id or self.slave_id
            result = self._client.read_holding_registers(address, count=2, device_id=sid)
            if result and not result.isError():
                value = (result.registers[0] << 16) | result.registers[1]
                self.reset_error()
                return value
            logger.error(f"读32位失败: {result}")
            self.increment_error()
            return None
        except Exception as e:
            logger.error(f"读32位异常: {e}")
            self.increment_error()
            return None

    def write_registers(self, address: int, values: list, slave_id: int = None) -> bool:
        """写多个寄存器"""
        if not self._ensure_connected():
            raise ConnectionError("Modbus 未连接且重连失败")
        try:
            sid = slave_id or self.slave_id
            result = self._client.write_registers(address, values, device_id=sid)
            if result and not result.isError():
                self.reset_error()
                return True
            logger.error(f"写多个寄存器失败: {result}")
            self.increment_error()
            return False
        except Exception as e:
            logger.error(f"写多个寄存器异常: {e}")
            self.increment_error()
            return False

    def write_long(self, address: int, value: int, slave_id: int = None) -> bool:
        """写 32 位数据"""
        if not self._ensure_connected():
            raise ConnectionError("Modbus 未连接且重连失败")
        try:
            sid = slave_id or self.slave_id
            high = (value >> 16) & 0xFFFF
            low = value & 0xFFFF
            result = self._client.write_registers(address, [high, low], device_id=sid)
            if result and not result.isError():
                self.reset_error()
                return True
            logger.error(f"写32位失败: {result}")
            self.increment_error()
            return False
        except Exception as e:
            logger.error(f"写32位异常: {e}")
            self.increment_error()
            return False

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        base = super().health_check()
        base.update({
            'protocol': 'modbus',
            'mode': self.mode,
            'slave_id': self.slave_id,
        })
        return base