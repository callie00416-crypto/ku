"""ATA-101B功率放大器驱动（自定义ASCII协议）

【组合关系】
ATA101BPowerAmplifier -> CustomAsciiProtocol -> SerialComm

【架构集成】
- 继承 BaseDevice 基类
- 支持平台设备生命周期管理
- 集成平台事件系统
- 符合工业设备规范

【设备信息】
- 厂商：安泰电子
- 型号：ATA-101B
- 协议：自定义ASCII
- 通信：USB串口（内置USB转串口芯片）
- 通道数：1
- 增益范围：0-20dB（步进2dB）
- 输入电阻：50Ω/1000Ω
- 输出电阻：1.5Ω/50Ω

【协议特点】
- 自定义ASCII协议
- 指令格式：ATA,SET,<CMD>;
- 响应格式：ASCII字符串
"""
from typing import Dict, Any, Optional
import logging
import time

from shared.drivers.base.base_device import BaseDevice

logger = logging.getLogger(__name__)


class ATA101BPowerAmplifier(BaseDevice):
    """安泰ATA-101B功率放大器驱动（符合新框架）
    
    【使用示例】
    >>> from shared.drivers.comm.serial_comm import SerialComm
    >>> from shared.drivers.protocol.custom_ascii import CustomAsciiProtocol
    >>> from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier
    >>> 
    >>> comm = SerialComm(driver_id='serial_pa', port='COM7', baudrate=115200)
    >>> protocol = CustomAsciiProtocol(driver_id='ascii_pa', comm=comm)
    >>> pa = ATA101BPowerAmplifier(driver_id='power_amplifier', protocol=protocol)
    >>> pa.connect()
    >>> pa.output_on()
    >>> pa.set_gain(20)
    >>> pa.output_off()
    >>> pa.disconnect()
    """
    
    # 命令常量
    COMMAND_PREFIX = 'ATA,SET,'
    COMMAND_SUFFIX = ';'
    RESPONSE_SUCCESS = 'SET DONE!'
    RESPONSE_ERROR = 'SET ERROR!'
    RESPONSE_OVER_RANGE = 'OVER RANGE ERROR!'
    
    # 增益范围
    MIN_GAIN = 0
    MAX_GAIN = 20
    GAIN_STEP = 2
    
    def __init__(self, driver_id: str = 'power_amplifier', protocol=None, 
                 platform_device=None, **kwargs):
        """
        Args:
            driver_id: 驱动ID
            protocol: 协议对象（CustomAsciiProtocol）
            platform_device: 平台设备对象（可选）
            **kwargs: 其他参数
        """
        super().__init__(driver_id, protocol, **kwargs)
        self._protocol = protocol
        self.platform_device = platform_device
        
        # 设备信息
        self._device_info = {
            'manufacturer': '安泰电子',
            'model': 'ATA-101B',
            'protocol': 'custom_ascii',
            'communication': 'usb_serial',
            'channels': 1,
            'max_gain': 20,
            'input_resistance_options': [50.0, 1000.0],
            'output_resistance_options': [1.5, 50.0]
        }
        
        # 命令映射
        self._commands = {
            'output_on': {
                'set': 'AON,0000',
                'description': '打开输出'
            },
            'output_off': {
                'set': 'AOF,0000',
                'description': '关闭输出'
            },
            'save_settings': {
                'set': 'SAV,0000',
                'description': '保存设置'
            },
            'input_resistance': {
                'set': 'RIN,{value}',
                'description': '设置输入电阻',
                'value_mapping': {'50': '0050', '1000': '1000'}
            },
            'output_resistance': {
                'set': 'ROT,{value}',
                'description': '设置输出电阻',
                'value_mapping': {'1.5': '0015', '50': '0500'}
            },
            'gain': {
                'set': 'AMP,{value}',
                'description': '设置增益',
                'value_mapping': {'0': '0000', '6': '0006', '12': '0012', '20': '0020'}
            }
        }
        
        # 当前状态
        self._state = {
            'output_enabled': False,
            'input_resistance': 50.0,
            'output_resistance': 50.0,
            'gain': 0
        }
        
        logger.info(f"ATA-101B功率放大器初始化完成: {driver_id}")
    
    def _build_command(self, command_key: str, value: str = None) -> str:
        """构建命令字符串（不包含前缀和后缀）"""
        if command_key not in self._commands:
            raise ValueError(f"未知命令: {command_key}")
        
        command_template = self._commands[command_key]['set']
        
        if value is not None:
            command = command_template.format(value=value)
        else:
            command = command_template
        
        return command
    
    def _send_command(self, command: str) -> bool:
        """发送命令并检查响应"""
        try:
            logger.debug(f"发送命令: {command}")
            
            response = self._protocol.send_command(command)
            
            if response == self.RESPONSE_SUCCESS:
                logger.debug(f"命令执行成功: {command}")
                return True
            elif response == self.RESPONSE_OVER_RANGE:
                logger.error(f"参数越界: {command}")
                return False
            elif response == self.RESPONSE_ERROR:
                logger.error(f"命令错误: {command}")
                return False
            else:
                logger.warning(f"未知响应: {response}")
                return False
                
        except Exception as e:
            logger.error(f"发送命令失败: {e}")
            self.increment_error()
            return False
    
    def output_on(self) -> bool:
        """打开输出"""
        if not self.is_connected:
            raise ConnectionError("功率放大器未连接")
        
        try:
            command = self._build_command('output_on')
            success = self._send_command(command)
            
            if success:
                self._state['output_enabled'] = True
                logger.info("功率放大器输出已打开")
            
            return success
            
        except Exception as e:
            logger.error(f"打开输出失败: {e}")
            self.increment_error()
            return False
    
    def output_off(self) -> bool:
        """关闭输出"""
        if not self.is_connected:
            raise ConnectionError("功率放大器未连接")
        
        try:
            command = self._build_command('output_off')
            success = self._send_command(command)
            
            if success:
                self._state['output_enabled'] = False
                logger.info("功率放大器输出已关闭")
            
            return success
            
        except Exception as e:
            logger.error(f"关闭输出失败: {e}")
            self.increment_error()
            return False
    
    def save_settings(self) -> bool:
        """保存设置"""
        if not self.is_connected:
            raise ConnectionError("功率放大器未连接")
        
        try:
            command = self._build_command('save_settings')
            success = self._send_command(command)
            
            if success:
                logger.info("功率放大器设置已保存")
            
            return success
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            self.increment_error()
            return False
    
    def set_input_resistance(self, resistance: float) -> bool:
        """设置输入电阻
        
        Args:
            resistance: 输入电阻值 (50Ω 或 1000Ω)
        
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("功率放大器未连接")
        
        try:
            valid_values = [50.0, 1000.0]
            if resistance not in valid_values:
                logger.error(f"无效的输入电阻值: {resistance}, 有效值: {valid_values}")
                return False
            
            value_mapping = self._commands['input_resistance']['value_mapping']
            value_str = value_mapping.get(str(int(resistance)))
            
            if not value_str:
                logger.error(f"无法映射电阻值: {resistance}")
                return False
            
            command = self._build_command('input_resistance', value_str)
            success = self._send_command(command)
            
            if success:
                self._state['input_resistance'] = resistance
                logger.info(f"输入电阻已设置: {resistance}Ω")
            
            return success
            
        except Exception as e:
            logger.error(f"设置输入电阻失败: {e}")
            self.increment_error()
            return False
    
    def set_output_resistance(self, resistance: float) -> bool:
        """设置输出电阻
        
        Args:
            resistance: 输出电阻值 (1.5Ω 或 50Ω)
        
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("功率放大器未连接")
        
        try:
            valid_values = [1.5, 50.0]
            if resistance not in valid_values:
                logger.error(f"无效的输出电阻值: {resistance}, 有效值: {valid_values}")
                return False
            
            value_mapping = self._commands['output_resistance']['value_mapping']
            value_str = value_mapping.get(str(resistance)) or \
                        value_mapping.get(str(int(resistance))) or \
                        value_mapping.get(f"{resistance:.1f}")
            
            if not value_str:
                logger.error(f"无法映射电阻值: {resistance}")
                return False
            
            command = self._build_command('output_resistance', value_str)
            success = self._send_command(command)
            
            if success:
                self._state['output_resistance'] = resistance
                logger.info(f"输出电阻已设置: {resistance}Ω")
            
            return success
            
        except Exception as e:
            logger.error(f"设置输出电阻失败: {e}")
            self.increment_error()
            return False
    
    def set_gain(self, gain_db: int) -> bool:
        """设置增益
        
        Args:
            gain_db: 增益值 (0-20dB, 步进2dB)
        
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("功率放大器未连接")
        
        try:
            if gain_db < self.MIN_GAIN or gain_db > self.MAX_GAIN:
                logger.error(f"增益值超出范围: {gain_db}, 范围: {self.MIN_GAIN}-{self.MAX_GAIN}dB")
                return False
            
            if gain_db % self.GAIN_STEP != 0:
                logger.error(f"增益值不符合步进要求: {gain_db}, 步进: {self.GAIN_STEP}dB")
                return False
            
            value_mapping = self._commands['gain']['value_mapping']
            value_str = value_mapping.get(str(gain_db))
            
            if not value_str:
                logger.error(f"无法映射增益值: {gain_db}")
                return False
            
            command = self._build_command('gain', value_str)
            success = self._send_command(command)
            
            if success:
                self._state['gain'] = gain_db
                logger.info(f"增益已设置: {gain_db}dB")
            
            return success
            
        except Exception as e:
            logger.error(f"设置增益失败: {e}")
            self.increment_error()
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        status = {
            'driver_id': self.driver_id,
            'output_enabled': self._state['output_enabled'],
            'input_resistance': self._state['input_resistance'],
            'output_resistance': self._state['output_resistance'],
            'gain': self._state['gain'],
            'device_info': self._device_info,
            'timestamp': time.time()
        }
        return status
    
    def connect(self) -> bool:
        """连接设备
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        try:
            self._device_status = "connecting"
            
            if not self._protocol.connect():
                self._device_status = "fault"
                if self.platform_device:
                    self.platform_device.disconnect()
                return False
            
            self._is_connected = True
            self._device_status = "connected"
            
            if self.platform_device:
                self.platform_device.connect()
            
            logger.info(f"ATA-101B功率放大器连接成功: {self.driver_id}")
            return True
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            self._device_status = "fault"
            self.increment_error()
            
            if self.platform_device:
                self.platform_device.disconnect()
            
            return False
    
    def disconnect(self):
        """断开设备
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        try:
            if self._state['output_enabled']:
                self.output_off()
            
            self._is_connected = False
            self._device_status = "disconnected"
            
            if self._protocol:
                self._protocol.disconnect()
            
            if self.platform_device:
                self.platform_device.disconnect()
            
            logger.info(f"ATA-101B功率放大器已断开: {self.driver_id}")
            
        except Exception as e:
            logger.error(f"断开失败: {e}")
    
    def reset(self) -> bool:
        """重置设备"""
        try:
            self.output_off()
            
            self._state = {
                'output_enabled': False,
                'input_resistance': 50.0,
                'output_resistance': 50.0,
                'gain': 0
            }
            
            self.reset_error()
            logger.info(f"ATA-101B功率放大器已重置: {self.driver_id}")
            return True
            
        except Exception as e:
            logger.error(f"重置失败: {e}")
            self.increment_error()
            return False
    
    def read_data(self) -> Dict[str, Any]:
        """读取设备核心数据"""
        if not self.is_connected:
            raise ConnectionError("功率放大器未连接")
        
        try:
            data = self.get_status()
            
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return data
            
        except Exception as e:
            logger.error(f"读取数据失败: {e}")
            self.increment_error()
            
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return {}
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据"""
        if not self.is_connected:
            raise ConnectionError("功率放大器未连接")
        
        try:
            success = True
            
            if 'gain' in data:
                if not self.set_gain(data['gain']):
                    success = False
            
            if 'input_resistance' in data:
                if not self.set_input_resistance(data['input_resistance']):
                    success = False
            
            if 'output_resistance' in data:
                if not self.set_output_resistance(data['output_resistance']):
                    success = False
            
            if 'output_enabled' in data:
                if data['output_enabled']:
                    if not self.output_on():
                        success = False
                else:
                    if not self.output_off():
                        success = False
            
            if self.platform_device:
                self.platform_device.record_operation(success=success)
            
            return success
            
        except Exception as e:
            logger.error(f"写入数据失败: {e}")
            self.increment_error()
            
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
    
    @property
    def device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        return self._device_info.copy()
    
    @property
    def state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return self._state.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        base = super().health_check()
        base.update({
            'device_type': 'power_amplifier',
            'device_info': self._device_info,
            'state': self._state
        })
        return base