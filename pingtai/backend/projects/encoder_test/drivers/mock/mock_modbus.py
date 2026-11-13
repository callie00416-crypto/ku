"""
Mock Modbus 驱动 - 用于测试的模拟协议驱动

【架构】
MockModbusDriver(BaseProtocol) - 继承自 BaseProtocol，模拟 Modbus 协议通信

支持：
- 寄存器读写
- 32 位数据读写
- 自动响应函数
- 预设寄存器值
"""
import logging
from typing import Optional, Dict, Any, Callable
from shared.drivers.base.base_protocol import BaseProtocol

logger = logging.getLogger(__name__)


class MockModbusDriver(BaseProtocol):
    """Mock Modbus 协议驱动"""
    
    def __init__(self, driver_id: str = 'mock_modbus', comm=None,
                 slave_id: int = 1, mode: str = 'rtu', **kwargs):
        """
        初始化 Mock Modbus 驱动
        
        Args:
            driver_id: 驱动唯一标识
            comm: 通讯层实例（可选）
            slave_id: 从站地址，默认 1
            mode: 协议模式，'rtu' 或 'tcp'，默认 'rtu'
            **kwargs: 其他配置参数
        """
        super().__init__(driver_id, comm, **kwargs)
        self.slave_id = slave_id
        self.mode = mode
        self._registers: Dict[int, int] = {}
        self._auto_responses: Dict[int, Callable] = {}
    
    def connect(self) -> bool:
        """连接（Mock 始终成功）"""
        self._is_connected = True
        logger.info(f"Mock Modbus 连接成功: slave_id={self.slave_id}, mode={self.mode}")
        return True
    
    def disconnect(self):
        """断开连接"""
        self._is_connected = False
        self._registers.clear()
        self._auto_responses.clear()
        logger.info(f"Mock Modbus 已断开")
    
    def is_connected(self) -> bool:
        """检查是否连接"""
        return self._is_connected
    
    def read_register(self, address: int, slave_id: int = None) -> Optional[int]:
        """
        读单个寄存器
        
        Args:
            address: 寄存器地址
            slave_id: 从站地址（可选，默认使用实例的 slave_id）
            
        Returns:
            寄存器值，如果地址不存在返回 0
        """
        actual_slave = slave_id if slave_id is not None else self.slave_id
        logger.debug(f"Mock Modbus 读寄存器: addr={address}, slave={actual_slave}")
        
        if address in self._auto_responses:
            return self._auto_responses[address]()
        
        return self._registers.get(address, 0)
    
    def read_registers(self, address: int, count: int = 1, slave_id: int = None) -> Optional[list]:
        """
        读多个寄存器
        
        Args:
            address: 起始寄存器地址
            count: 读取数量，默认 1
            slave_id: 从站地址（可选）
            
        Returns:
            寄存器值列表
        """
        actual_slave = slave_id if slave_id is not None else self.slave_id
        logger.debug(f"Mock Modbus 读多个寄存器: addr={address}, count={count}, slave={actual_slave}")
        
        result = []
        for i in range(count):
            addr = address + i
            if addr in self._auto_responses:
                result.append(self._auto_responses[addr]())
            else:
                result.append(self._registers.get(addr, 0))
        return result
    
    def write_register(self, address: int, value: int, slave_id: int = None) -> bool:
        """
        写单个寄存器
        
        Args:
            address: 寄存器地址
            value: 要写入的值
            slave_id: 从站地址（可选）
            
        Returns:
            写入是否成功
        """
        actual_slave = slave_id if slave_id is not None else self.slave_id
        logger.debug(f"Mock Modbus 写寄存器: addr={address}, value={value}, slave={actual_slave}")
        
        self._registers[address] = value & 0xFFFF  # 确保是 16 位值
        return True
    
    def write_registers(self, address: int, values: list, slave_id: int = None) -> bool:
        """
        写多个寄存器
        
        Args:
            address: 起始寄存器地址
            values: 要写入的值列表
            slave_id: 从站地址（可选）
            
        Returns:
            写入是否成功
        """
        actual_slave = slave_id if slave_id is not None else self.slave_id
        logger.debug(f"Mock Modbus 写多个寄存器: addr={address}, count={len(values)}, slave={actual_slave}")
        
        for i, value in enumerate(values):
            self._registers[address + i] = value & 0xFFFF
        return True
    
    def read_long(self, address: int, slave_id: int = None) -> Optional[int]:
        """
        读 32 位数据（两个连续寄存器）
        
        Args:
            address: 低位寄存器地址
            slave_id: 从站地址（可选）
            
        Returns:
            32 位整数值
        """
        actual_slave = slave_id if slave_id is not None else self.slave_id
        logger.debug(f"Mock Modbus 读 32 位数据: addr={address}, slave={actual_slave}")
        
        high = self._registers.get(address + 1, 0)
        low = self._registers.get(address, 0)
        return (high << 16) | low
    
    def write_long(self, address: int, value: int, slave_id: int = None) -> bool:
        """
        写 32 位数据（两个连续寄存器）
        
        Args:
            address: 低位寄存器地址
            value: 要写入的 32 位值
            slave_id: 从站地址（可选）
            
        Returns:
            写入是否成功
        """
        actual_slave = slave_id if slave_id is not None else self.slave_id
        logger.debug(f"Mock Modbus 写 32 位数据: addr={address}, value={value}, slave={actual_slave}")
        
        self._registers[address] = value & 0xFFFF
        self._registers[address + 1] = (value >> 16) & 0xFFFF
        return True
    
    def set_register(self, address: int, value: int):
        """
        预设寄存器值（测试前设置初始状态）
        
        Args:
            address: 寄存器地址
            value: 预设值
        """
        self._registers[address] = value & 0xFFFF
        logger.debug(f"Mock Modbus 预设寄存器: addr={address}, value={value}")
    
    def set_long(self, address: int, value: int):
        """
        预设 32 位值（测试前设置初始状态）
        
        Args:
            address: 低位寄存器地址
            value: 预设的 32 位值
        """
        self._registers[address] = value & 0xFFFF
        self._registers[address + 1] = (value >> 16) & 0xFFFF
        logger.debug(f"Mock Modbus 预设 32 位值: addr={address}, value={value}")
    
    def set_auto_response(self, address: int, func: Callable):
        """
        设置自动响应函数（动态计算返回值）
        
        Args:
            address: 寄存器地址
            func: 无参数函数，返回寄存器值
        """
        self._auto_responses[address] = func
        logger.debug(f"Mock Modbus 设置自动响应: addr={address}")
    
    def clear_auto_responses(self):
        """清除所有自动响应函数"""
        self._auto_responses.clear()
        logger.debug("Mock Modbus 自动响应已清除")
    
    def get_register_count(self) -> int:
        """获取已设置的寄存器数量"""
        return len(self._registers)
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        base = super().health_check()
        base.update({
            'slave_id': self.slave_id,
            'mode': self.mode,
            'register_count': len(self._registers),
            'auto_response_count': len(self._auto_responses),
            'mock': True
        })
        return base