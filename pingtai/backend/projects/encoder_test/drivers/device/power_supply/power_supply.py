"""
电源设备 - 设备业务层

所属层级：Device 层
职责：可编程双路电源设备业务逻辑

【架构集成】
- 继承 shared/drivers/base/base_device.BaseDevice
- 通过 Adapter 集成平台 Device 领域模型
- 使用平台能力：生命周期管理、事件发布、状态机

【禁止】
- 直接操作串口/socket
- 处理协议帧
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import logging
import struct
from typing import Dict, Any, Optional
from shared.drivers.base.base_device import BaseDevice

logger = logging.getLogger(__name__)


class PowerSupply(BaseDevice):
    """可编程双路电源驱动（Modbus RTU）
    
    【组合关系】
    PowerSupply -> ModbusDriver -> RS485Comm
    
    【架构集成】
    - 继承 BaseDevice 基类
    - 支持平台设备生命周期管理
    - 集成平台事件系统
    - 符合工业设备规范
    
    【使用示例】
    >>> from shared.drivers.factory import CommFactory, ProtocolFactory, DeviceFactory
    >>> from projects.encoder_test.adapters.power_supply_adapter import PowerSupplyDeviceAdapter
    >>> 
    >>> # 创建平台设备
    >>> platform_device = PowerSupplyDeviceAdapter.to_platform_device(
    ...     station_id=1,
    ...     device_code="PS-001",
    ...     device_name="可编程双路电源"
    ... )
    >>> 
    >>> # 创建通信层
    >>> comm = CommFactory.create('rs485', port='COM4', baudrate=9600)
    >>> protocol = ProtocolFactory.create('modbus_rtu', comm=comm, slave_id=1)
    >>> 
    >>> # 创建设备驱动
    >>> ps = PowerSupply(driver_id='power_supply', protocol=protocol)
    >>> ps.connect()
    >>> ps.set_voltage(5.0, channel=1)
    """
    
    # Modbus寄存器地址定义（双路输出型号，地址偏移256）
    # 数据格式：unsigned long (32位整数)
    # 单位：电压mV（毫伏），电流mA（毫安）
    REG_REMOTE_MODE = 0x0000  # 远程/本地模式 (0=本地, 1=远程)
    
    # CH1 寄存器地址
    REG_V_SET = {1: 0x0101, 2: 0x010B}  # 通道1/2设定电压 (257/267)
    REG_I_SET = {1: 0x0103, 2: 0x010D}  # 通道1/2设定电流 (259/269)
    REG_V_OUT = {1: 0x0105, 2: 0x010F}  # 通道1/2输出电压 (261/271)
    REG_I_OUT = {1: 0x0107, 2: 0x0111}  # 通道1/2输出电流 (263/273)
    REG_OUTPUT = {1: 0x0109, 2: 0x0113}  # 通道1/2输出控制 (265/275) 0=开, 1=关
    REG_STATUS = {1: 0x010A, 2: 0x0114}  # 通道1/2CC/CV状态 (266/276) 1=CV, 0=CC
    
    def __init__(self, driver_id: str = 'power_supply', protocol=None, 
                 platform_device=None, **kwargs):
        """
        Args:
            driver_id: 驱动ID
            protocol: 协议对象
            platform_device: 平台设备对象（可选）
            **kwargs: 其他参数
        """
        super().__init__(driver_id, protocol, **kwargs)
        self.modbus = protocol
        self.platform_device = platform_device  # 平台设备集成
        
        # 电源特定状态
        self._channel_states = {
            1: {'voltage_set': 0.0, 'current_set': 0.0, 'output_enabled': False},
            2: {'voltage_set': 0.0, 'current_set': 0.0, 'output_enabled': False}
        }
        
        # 设备信息
        self._device_info = {
            'manufacturer': '博瑞',
            'model': '程控系列',
            'channels': 2,
            'max_voltage': 30.0,
            'max_current': 5.0
        }
    
    def connect(self) -> bool:
        """连接电源并进入远程模式
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        try:
            # 更新状态为连接中
            self._device_status = "connecting"
            
            # 连接协议层
            if not self.modbus.connect():
                self._device_status = "fault"
                if self.platform_device:
                    self.platform_device.disconnect()
                return False
            
            # 进入远程模式
            self.modbus.write_register(self.REG_REMOTE_MODE, 1)
            time.sleep(0.3)
            
            # 更新状态为已连接
            self._is_connected = True
            self._device_status = "connected"
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.connect()
            
            logger.info(f"电源连接成功: {self.driver_id}")
            return True
        except Exception as e:
            logger.error(f"电源连接失败: {e}")
            self._device_status = "fault"
            self.increment_error()
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.disconnect()
            
            return False
    
    def disconnect(self):
        """断开电源连接
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        self._is_connected = False
        self._device_status = "disconnected"
        
        # 断开协议层
        if self.modbus:
            self.modbus.disconnect()
        
        # 集成平台设备
        if self.platform_device:
            self.platform_device.disconnect()
        
        # 关闭所有通道输出
        self._channel_states[1]['output_enabled'] = False
        self._channel_states[2]['output_enabled'] = False
        
        logger.info(f"电源已断开: {self.driver_id}")
    
    @property
    def is_connected(self) -> bool:
        """检查电源是否连接"""
        return self._is_connected and self._device_status == "connected"
    
    def set_voltage(self, voltage: float, channel: int = 1) -> bool:
        """设置通道电压 (V)
        
        【架构集成】
        - 参数验证
        - 状态记录
        - 错误处理
        - 平台设备操作记录
        
        Args:
            voltage: 目标电压
            channel: 通道号 (1或2)
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电源未连接")
        
        # 参数验证
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if voltage < 0 or voltage > self._device_info['max_voltage']:
            raise ValueError(f"电压超出范围: 0-{self._device_info['max_voltage']}V")
        
        try:
            # 将电压转换为32位整数（单位：mV）
            voltage_mv = int(voltage * 1000)
            
            # 将32位整数拆分为两个16位整数（大端序）
            high_word = (voltage_mv >> 16) & 0xFFFF
            low_word = voltage_mv & 0xFFFF
            
            # 使用功能码0x10写两个寄存器
            self.modbus.write_registers(self.REG_V_SET[channel], [high_word, low_word])
            
            # 记录状态
            self._channel_states[channel]['voltage_set'] = voltage
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}电压设置为: {voltage}V")
            return True
        except Exception as e:
            logger.error(f"设置电压失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_current(self, current: float, channel: int = 1) -> bool:
        """设置通道电流 (A)
        
        【架构集成】
        - 参数验证
        - 状态记录
        - 错误处理
        - 平台设备操作记录
        
        Args:
            current: 目标电流
            channel: 通道号 (1或2)
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电源未连接")
        
        # 参数验证
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if current < 0 or current > self._device_info['max_current']:
            raise ValueError(f"电流超出范围: 0-{self._device_info['max_current']}A")
        
        try:
            # 将电流转换为32位整数（单位：mA）
            current_ma = int(current * 1000)
            
            # 将32位整数拆分为两个16位整数（大端序）
            high_word = (current_ma >> 16) & 0xFFFF
            low_word = current_ma & 0xFFFF
            
            # 使用功能码0x10写两个寄存器
            self.modbus.write_registers(self.REG_I_SET[channel], [high_word, low_word])
            
            # 记录状态
            self._channel_states[channel]['current_set'] = current
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}电流设置为: {current}A")
            return True
        except Exception as e:
            logger.error(f"设置电流失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def turn_on(self, channel: int = 1) -> bool:
        """打开通道输出
        
        注意：OUTPUT逻辑是 0=打开, 1=关闭（与常规相反）
        """
        if not self.is_connected:
            raise ConnectionError("电源未连接")
        try:
            # 写入0打开输出
            self.modbus.write_register(self.REG_OUTPUT[channel], 0)
            self._channel_states[channel]['output_enabled'] = True
            logger.info(f"通道{channel}输出已打开")
            return True
        except Exception as e:
            logger.error(f"打开通道失败: {e}")
            self.increment_error()
            return False
    
    def turn_off(self, channel: int = 1) -> bool:
        """关闭通道输出
        
        注意：OUTPUT逻辑是 0=打开, 1=关闭（与常规相反）
        """
        if not self.is_connected:
            raise ConnectionError("电源未连接")
        try:
            # 写入1关闭输出
            self.modbus.write_register(self.REG_OUTPUT[channel], 1)
            self._channel_states[channel]['output_enabled'] = False
            logger.info(f"通道{channel}输出已关闭")
            return True
        except Exception as e:
            logger.error(f"关闭通道失败: {e}")
            self.increment_error()
            return False
    
    def read_voltage(self, channel: int = 1) -> float:
        """读取实际输出电压 (V)
        
        数据格式：32位整数，单位mV
        """
        if not self.is_connected:
            raise ConnectionError("电源未连接")
        try:
            # 读取两个寄存器（32位整数格式）
            registers = self.modbus.read_registers(self.REG_V_OUT[channel], 2)
            if registers and len(registers) == 2:
                # 将两个16位整数合并为32位整数（大端序）
                high_word = registers[0]
                low_word = registers[1]
                voltage_mv = (high_word << 16) | low_word
                # 转换为V
                voltage = voltage_mv / 1000.0
                return voltage
            return 0.0
        except Exception as e:
            logger.error(f"读取电压失败: {e}")
            self.increment_error()
            return 0.0
    
    def read_current(self, channel: int = 1) -> float:
        """读取实际输出电流 (A)
        
        数据格式：32位整数，单位mA
        """
        if not self.is_connected:
            raise ConnectionError("电源未连接")
        try:
            # 读取两个寄存器（32位整数格式）
            registers = self.modbus.read_registers(self.REG_I_OUT[channel], 2)
            if registers and len(registers) == 2:
                # 将两个16位整数合并为32位整数（大端序）
                high_word = registers[0]
                low_word = registers[1]
                current_ma = (high_word << 16) | low_word
                # 转换为A
                current = current_ma / 1000.0
                return current
            return 0.0
        except Exception as e:
            logger.error(f"读取电流失败: {e}")
            self.increment_error()
            return 0.0
    
    def read_status(self, channel: int = 1) -> Dict[str, Any]:
        """读取通道状态"""
        try:
            voltage = self.read_voltage(channel)
            current = self.read_current(channel)
            status_reg = self.modbus.read_register(self.REG_STATUS[channel])
            is_cv = status_reg == 1 if status_reg is not None else False
            mode_str = "CV" if is_cv else "CC"
            return {
                'voltage': voltage,
                'current': current,
                'mode': mode_str,
                'channel': channel
            }
        except Exception as e:
            logger.error(f"读取状态失败: {e}")
            return {'channel': channel, 'error': str(e)}
    
    def read_data(self) -> Dict[str, Any]:
        """读取双通道完整数据"""
        ch1 = self.read_status(1)
        ch2 = self.read_status(2)
        return {'ch1': ch1, 'ch2': ch2}
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据"""
        try:
            channel = data.get('channel', 1)
            voltage = data.get('voltage')
            current = data.get('current')
            output = data.get('output')
            
            if voltage is not None:
                self.set_voltage(voltage, channel)
            if current is not None:
                self.set_current(current, channel)
            if output is not None:
                if output:
                    self.turn_on(channel)
                else:
                    self.turn_off(channel)
            return True
        except Exception as e:
            logger.error(f"写入数据失败: {e}")
            return False
    
    def reset(self):
        """重置设备"""
        self.disconnect()
        self.connect()
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查
        
        【架构集成】
        - 继承基类健康检查
        - 添加电源特定检查
        - 集成平台设备状态
        - 提供详细诊断信息
        
        Returns:
            健康状态字典
        """
        base = super().health_check()
        
        # 电源特定健康检查
        try:
            if self.is_connected:
                # 读取双通道状态
                ch1_status = self.read_status(1)
                ch2_status = self.read_status(2)
                
                # 更新平台设备心跳
                if self.platform_device:
                    self.platform_device.update_heartbeat()
                
                power_health = {
                    'device_type': 'power_supply',
                    'manufacturer': self._device_info['manufacturer'],
                    'model': self._device_info['model'],
                    'channels': self._device_info['channels'],
                    'channel_states': self._channel_states,
                    'real_time_status': {
                        'ch1': ch1_status,
                        'ch2': ch2_status
                    },
                    'protocol_driver_id': self.modbus.driver_id if self.modbus else None,
                    'platform_device_id': self.platform_device.id if self.platform_device else None,
                    'platform_device_connected': self.platform_device.is_connected if self.platform_device else False
                }
            else:
                power_health = {
                    'device_type': 'power_supply',
                    'manufacturer': self._device_info['manufacturer'],
                    'model': self._device_info['model'],
                    'channels': self._device_info['channels'],
                    'channel_states': self._channel_states,
                    'status': 'disconnected',
                    'protocol_driver_id': self.modbus.driver_id if self.modbus else None,
                    'platform_device_id': self.platform_device.id if self.platform_device else None,
                    'platform_device_connected': False
                }
        except Exception as e:
            logger.error(f"健康检查异常: {e}")
            power_health = {
                'device_type': 'power_supply',
                'status': 'error',
                'error': str(e),
                'protocol_driver_id': self.modbus.driver_id if self.modbus else None,
                'platform_device_id': self.platform_device.id if self.platform_device else None
            }
        
        base.update(power_health)
        return base
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息
        
        Returns:
            设备信息字典
        """
        return {
            'driver_id': self.driver_id,
            'device_info': self._device_info,
            'channel_states': self._channel_states,
            'is_connected': self.is_connected,
            'device_status': self._device_status,
            'error_count': self._error_count,
            'platform_device': {
                'id': self.platform_device.id if self.platform_device else None,
                'code': self.platform_device.code if self.platform_device else None,
                'name': self.platform_device.name if self.platform_device else None,
                'is_connected': self.platform_device.is_connected if self.platform_device else False,
                'is_heartbeat_alive': self.platform_device.is_heartbeat_alive if self.platform_device else False
            } if self.platform_device else None
        }
    
    def reset(self):
        """重置设备
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 重置所有状态
        - 集成平台设备重置
        """
        logger.info(f"重置电源设备: {self.driver_id}")
        
        # 关闭所有输出
        for channel in [1, 2]:
            try:
                self.turn_off(channel)
            except Exception as e:
                logger.warning(f"关闭通道{channel}失败: {e}")
        
        # 重置状态
        self._channel_states = {
            1: {'voltage_set': 0.0, 'current_set': 0.0, 'output_enabled': False},
            2: {'voltage_set': 0.0, 'current_set': 0.0, 'output_enabled': False}
        }
        
        # 重置错误计数
        self.reset_error()
        
        # 集成平台设备重置
        if self.platform_device:
            try:
                self.platform_device.disconnect()
                self.platform_device.connect()
            except Exception as e:
                logger.warning(f"平台设备重置失败: {e}")
        
        # 重新连接
        self.disconnect()
        time.sleep(1.0)
        self.connect()
        
        logger.info(f"电源设备重置完成: {self.driver_id}")