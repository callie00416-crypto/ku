"""
RIGOL DG811波形发生器 - 设备业务层

所属层级：Device 层
职责：RIGOL DG811波形发生器业务逻辑

【架构集成】
- 继承 shared/drivers/base/base_device.BaseDevice
- 通过 Adapter 集成平台 Device 领域模型
- 使用平台能力：生命周期管理、事件发布、状态机

【设备特性】
- 双通道输出
- 支持多种波形：正弦波、方波、三角波、锯齿波、脉冲、噪声等
- 频率范围：1μHz ~ 25MHz
- 幅度范围：-20Vpp ~ +20Vpp
- USB连接（USBTMC）

【使用示例】
>>> from shared.drivers.comm.usb_comm import USBComm
>>> from shared.drivers.protocol.scpi_protocol import SCPIProtocol
>>> from projects.encoder_test.drivers.device.waveform_generator.dg811 import DG811WaveformGenerator
>>> 
>>> # 创建通信层
>>> comm = USBComm(driver_id='usb_tmc', vid=0x0914, pid=0x0001)
>>> comm.open()
>>> 
>>> # 创建协议层
>>> protocol = SCPIProtocol(driver_id='scpi', comm=comm)
>>> 
>>> # 创建设备驱动
>>> generator = DG811WaveformGenerator(driver_id='dg811', protocol=protocol)
>>> generator.connect()
>>> 
>>> # 设置波形
>>> generator.set_waveform('SIN', frequency=1000, amplitude=5.0, offset=0.0, channel=1)
>>> generator.output_on(channel=1)
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import logging
from typing import Dict, Any, Optional, List
from shared.drivers.base.base_device import BaseDevice

logger = logging.getLogger(__name__)


class DG811WaveformGenerator(BaseDevice):
    """RIGOL DG811波形发生器驱动（SCPI协议）
    
    【组合关系】
    DG811WaveformGenerator -> SCPIProtocol -> USBComm
    
    【架构集成】
    - 继承 BaseDevice 基类
    - 支持平台设备生命周期管理
    - 集成平台事件系统
    - 符合工业设备规范
    
    【设备信息】
    - 厂商：RIGOL
    - 型号：DG811
    - 通道：双通道
    - 频率范围：1μHz ~ 25MHz
    - 幅度范围：-20Vpp ~ +20Vpp
    """
    
    # 波形类型
    WAVEFORM_SIN = 'SIN'      # 正弦波
    WAVEFORM_SQU = 'SQU'      # 方波
    WAVEFORM_TRI = 'TRI'      # 三角波
    WAVEFORM_RAMP = 'RAMP'    # 锯齿波
    WAVEFORM_PULS = 'PULS'    # 脉冲
    WAVEFORM_NOIS = 'NOIS'    # 噪声
    WAVEFORM_PRBS = 'PRBS'    # 伪随机序列
    WAVEFORM_ARB = 'ARB'      # 任意波
    
    WAVEFORM_TYPES = [
        WAVEFORM_SIN, WAVEFORM_SQU, WAVEFORM_TRI, 
        WAVEFORM_RAMP, WAVEFORM_PULS, WAVEFORM_NOIS, 
        WAVEFORM_PRBS, WAVEFORM_ARB
    ]
    
    # 频率范围
    MIN_FREQUENCY = 1e-6      # 1μHz
    MAX_FREQUENCY = 25e6     # 25MHz
    
    # 幅度范围
    MIN_AMPLITUDE = 0.01     # 10mVpp
    MAX_AMPLITUDE = 20.0     # 20Vpp
    
    # 偏置范围
    MIN_OFFSET = -10.0       # -10V
    MAX_OFFSET = 10.0        # +10V
    
    def __init__(self, driver_id: str = 'dg811', protocol=None, 
                 platform_device=None, **kwargs):
        """
        Args:
            driver_id: 驱动ID
            protocol: 协议对象（SCPIProtocol）
            platform_device: 平台设备对象（可选）
            **kwargs: 其他参数
        """
        super().__init__(driver_id, protocol, **kwargs)
        self.scpi = protocol
        self.platform_device = platform_device
        
        # 通道状态
        self._channel_states = {
            1: {
                'waveform': self.WAVEFORM_SIN,
                'frequency': 1000.0,
                'amplitude': 1.0,
                'offset': 0.0,
                'phase': 0.0,
                'output_enabled': False
            },
            2: {
                'waveform': self.WAVEFORM_SIN,
                'frequency': 1000.0,
                'amplitude': 1.0,
                'offset': 0.0,
                'phase': 0.0,
                'output_enabled': False
            }
        }
        
        # 设备信息
        self._device_info = {
            'manufacturer': 'RIGOL',
            'model': 'DG811',
            'channels': 2,
            'max_frequency': 25e6,
            'max_amplitude': 20.0,
            'max_offset': 10.0
        }
    
    def connect(self) -> bool:
        """连接波形发生器
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        try:
            # 更新状态为连接中
            self._device_status = "connecting"
            
            # 连接协议层
            if not self.scpi.connect():
                self._device_status = "fault"
                if self.platform_device:
                    self.platform_device.disconnect()
                return False
            
            # 清除错误队列
            self.scpi.clear()
            time.sleep(0.1)
            
            # 获取设备ID
            device_id = self.scpi.get_id()
            if device_id:
                logger.info(f"设备ID: {device_id}")
            
            # 更新状态为已连接
            self._is_connected = True
            self._device_status = "connected"
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.connect()
            
            logger.info(f"波形发生器连接成功: {self.driver_id}")
            return True
        except Exception as e:
            logger.error(f"波形发生器连接失败: {e}")
            self._device_status = "fault"
            self.increment_error()
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.disconnect()
            
            return False
    
    def disconnect(self):
        """断开波形发生器连接
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        # 关闭所有输出
        for channel in [1, 2]:
            try:
                self.output_off(channel)
            except Exception as e:
                logger.warning(f"关闭通道{channel}输出失败: {e}")
        
        self._is_connected = False
        self._device_status = "disconnected"
        
        # 断开协议层
        if self.scpi:
            self.scpi.disconnect()
        
        # 集成平台设备
        if self.platform_device:
            self.platform_device.disconnect()
        
        # 关闭所有通道输出
        self._channel_states[1]['output_enabled'] = False
        self._channel_states[2]['output_enabled'] = False
        
        logger.info(f"波形发生器已断开: {self.driver_id}")
    
    @property
    def is_connected(self) -> bool:
        """检查波形发生器是否连接"""
        return self._is_connected and self._device_status == "connected"
    
    def set_waveform(self, waveform: str, frequency: float = 1000.0, 
                     amplitude: float = None, offset: float = None, 
                     phase: float = 0.0, channel: int = 1) -> bool:
        """设置波形参数
        
        【架构集成】
        - 参数验证
        - 状态记录
        - 错误处理
        - 平台设备操作记录
        
        Args:
            waveform: 波形类型（SIN/SQU/TRI/RAMP/PULS/NOIS/PRBS/ARB）
            frequency: 频率（Hz）
            amplitude: 幅度（Vpp，可选，为None时不设置）
            offset: 偏置（V，可选，为None时不设置）
            phase: 相位（度）
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        # 参数验证
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if waveform not in self.WAVEFORM_TYPES:
            raise ValueError(f"无效波形类型: {waveform}")
        
        if frequency < self.MIN_FREQUENCY or frequency > self.MAX_FREQUENCY:
            raise ValueError(f"频率超出范围: {self.MIN_FREQUENCY}-{self.MAX_FREQUENCY}Hz")
        
        if amplitude is not None and (amplitude < self.MIN_AMPLITUDE or amplitude > self.MAX_AMPLITUDE):
            raise ValueError(f"幅度超出范围: {self.MIN_AMPLITUDE}-{self.MAX_AMPLITUDE}Vpp")
        
        if offset is not None and (offset < self.MIN_OFFSET or offset > self.MAX_OFFSET):
            raise ValueError(f"偏置超出范围: {self.MIN_OFFSET}-{self.MAX_OFFSET}V")
        
        try:
            # 设置波形类型
            self.scpi.write(f':SOUR{channel}:FUNC {waveform}')
            
            # 设置频率
            self.scpi.write(f':SOUR{channel}:FREQ {frequency}')
            
            # 设置幅度（如果提供）
            if amplitude is not None:
                self.scpi.write(f':SOUR{channel}:VOLT {amplitude}')
            
            # 设置偏置（如果提供）
            if offset is not None:
                self.scpi.write(f':SOUR{channel}:VOLT:OFFS {offset}')
            
            # 设置相位
            self.scpi.write(f':SOUR{channel}:PHAS {phase}')
            
            # 记录状态
            self._channel_states[channel]['waveform'] = waveform
            self._channel_states[channel]['frequency'] = frequency
            if amplitude is not None:
                self._channel_states[channel]['amplitude'] = amplitude
            if offset is not None:
                self._channel_states[channel]['offset'] = offset
            self._channel_states[channel]['phase'] = phase
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}波形设置: {waveform}, {frequency}Hz, "
                       f"{amplitude if amplitude is not None else 'N/A'}Vpp, "
                       f"{offset if offset is not None else 'N/A'}V, {phase}°")
            return True
            
        except Exception as e:
            logger.error(f"设置波形失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_frequency(self, frequency: float, channel: int = 1) -> bool:
        """设置频率
        
        Args:
            frequency: 频率（Hz）
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if frequency < self.MIN_FREQUENCY or frequency > self.MAX_FREQUENCY:
            raise ValueError(f"频率超出范围: {self.MIN_FREQUENCY}-{self.MAX_FREQUENCY}Hz")
        
        try:
            self.scpi.write(f':SOUR{channel}:FREQ {frequency}')
            self._channel_states[channel]['frequency'] = frequency
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}频率设置为: {frequency}Hz")
            return True
            
        except Exception as e:
            logger.error(f"设置频率失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_amplitude(self, amplitude: float, channel: int = 1) -> bool:
        """设置幅度
        
        Args:
            amplitude: 幅度（Vpp）
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if amplitude < self.MIN_AMPLITUDE or amplitude > self.MAX_AMPLITUDE:
            raise ValueError(f"幅度超出范围: {self.MIN_AMPLITUDE}-{self.MAX_AMPLITUDE}Vpp")
        
        try:
            self.scpi.write(f':SOUR{channel}:VOLT {amplitude}')
            self._channel_states[channel]['amplitude'] = amplitude
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}幅度设置为: {amplitude}Vpp")
            return True
            
        except Exception as e:
            logger.error(f"设置幅度失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_offset(self, offset: float, channel: int = 1) -> bool:
        """设置偏置
        
        Args:
            offset: 偏置（V）
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if offset < self.MIN_OFFSET or offset > self.MAX_OFFSET:
            raise ValueError(f"偏置超出范围: {self.MIN_OFFSET}-{self.MAX_OFFSET}V")
        
        try:
            self.scpi.write(f':SOUR{channel}:VOLT:OFFS {offset}')
            self._channel_states[channel]['offset'] = offset
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}偏置设置为: {offset}V")
            return True
            
        except Exception as e:
            logger.error(f"设置偏置失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_high_low_level(self, high_level: float, low_level: float, channel: int = 1) -> bool:
        """设置方波高低电平（High/Low模式）
        
        Args:
            high_level: 高电平（V）
            low_level: 低电平（V）
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if high_level < -10 or high_level > 10:
            raise ValueError(f"高电平超出范围: -10~10V")
        
        if low_level < -10 or low_level > 10:
            raise ValueError(f"低电平超出范围: -10~10V")
        
        if high_level <= low_level:
            raise ValueError(f"高电平必须大于低电平: {high_level} <= {low_level}")
        
        try:
            self.scpi.write(f':SOUR{channel}:VOLT:HIGH {high_level}')
            self.scpi.write(f':SOUR{channel}:VOLT:LOW {low_level}')
            
            # 查询验证设置是否成功
            actual_high = float(self.scpi.query(f':SOUR{channel}:VOLT:HIGH?'))
            actual_low = float(self.scpi.query(f':SOUR{channel}:VOLT:LOW?'))
            
            if abs(actual_high - high_level) > 0.01 or abs(actual_low - low_level) > 0.01:
                logger.warning(f"通道{channel}高低电平设置验证失败: "
                             f"期望 High={high_level}V, Low={low_level}V, "
                             f"实际 High={actual_high}V, Low={actual_low}V")
            
            self._channel_states[channel]['high_level'] = high_level
            self._channel_states[channel]['low_level'] = low_level
            
            # 根据High/Low计算幅度和偏置
            calculated_amplitude = high_level - low_level
            calculated_offset = (high_level + low_level) / 2.0
            self._channel_states[channel]['amplitude'] = calculated_amplitude
            self._channel_states[channel]['offset'] = calculated_offset
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}高低电平设置: High={high_level}V, Low={low_level}V "
                       f"(幅度={calculated_amplitude}Vpp, 偏置={calculated_offset}V) "
                       f"[验证: High={actual_high}V, Low={actual_low}V]")
            return True
            
        except Exception as e:
            logger.error(f"设置高低电平失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_duty_cycle(self, duty_cycle: float, channel: int = 1) -> bool:
        """设置占空比（方波）
        
        Args:
            duty_cycle: 占空比（0-100%）
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError(f"占空比超出范围: 0-100%")
        
        try:
            self.scpi.write(f':SOUR{channel}:FUNC:SQU:DCYC {duty_cycle}')
            self._channel_states[channel]['duty_cycle'] = duty_cycle
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}占空比设置为: {duty_cycle}%")
            return True
            
        except Exception as e:
            logger.error(f"设置占空比失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_output_impedance(self, impedance: str, channel: int = 1) -> bool:
        """设置输出阻抗（负载）
        
        Args:
            impedance: 阻抗类型 ('50' 或 'HZ' for High-Z)
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if impedance not in ['50', 'HZ']:
            raise ValueError(f"阻抗类型错误: {impedance}，应为 '50' 或 'HZ'")
        
        try:
            cmd = f':OUTP{channel}:IMP {impedance}'
            self.scpi.write(cmd)
            self._channel_states[channel]['output_impedance'] = impedance
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}输出阻抗设置为: {impedance}")
            return True
            
        except Exception as e:
            logger.error(f"设置输出阻抗失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_phase(self, phase: float, channel: int = 1) -> bool:
        """设置相位
        
        Args:
            phase: 相位（度）
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        if phase < 0 or phase > 360:
            raise ValueError(f"相位超出范围: 0-360°")
        
        try:
            self.scpi.write(f':SOUR{channel}:PHAS {phase}')
            self._channel_states[channel]['phase'] = phase
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"通道{channel}相位设置为: {phase}°")
            return True
            
        except Exception as e:
            logger.error(f"设置相位失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def output_on(self, channel: int = 1) -> bool:
        """打开通道输出
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        try:
            self.scpi.write(f':OUTP{channel} ON')
            self._channel_states[channel]['output_enabled'] = True
            logger.info(f"通道{channel}输出已打开")
            return True
            
        except Exception as e:
            logger.error(f"打开通道输出失败: {e}")
            self.increment_error()
            return False
    
    def output_off(self, channel: int = 1) -> bool:
        """关闭通道输出
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        if channel not in [1, 2]:
            raise ValueError(f"无效通道号: {channel}")
        
        try:
            self.scpi.write(f':OUTP{channel} OFF')
            self._channel_states[channel]['output_enabled'] = False
            logger.info(f"通道{channel}输出已关闭")
            return True
            
        except Exception as e:
            logger.error(f"关闭通道输出失败: {e}")
            self.increment_error()
            return False
    
    def get_frequency(self, channel: int = 1) -> Optional[float]:
        """获取频率
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            频率（Hz）
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        try:
            response = self.scpi.query(f':SOUR{channel}:FREQ?')
            if response:
                frequency = float(response)
                self._channel_states[channel]['frequency'] = frequency
                return frequency
            return None
            
        except Exception as e:
            logger.error(f"获取频率失败: {e}")
            self.increment_error()
            return None
    
    def get_amplitude(self, channel: int = 1) -> Optional[float]:
        """获取幅度
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            幅度（Vpp）
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        try:
            response = self.scpi.query(f':SOUR{channel}:VOLT?')
            if response:
                amplitude = float(response)
                self._channel_states[channel]['amplitude'] = amplitude
                return amplitude
            return None
            
        except Exception as e:
            logger.error(f"获取幅度失败: {e}")
            self.increment_error()
            return None
    
    def get_offset(self, channel: int = 1) -> Optional[float]:
        """获取偏置
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            偏置（V）
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        try:
            response = self.scpi.query(f':SOUR{channel}:VOLT:OFFS?')
            if response:
                offset = float(response)
                self._channel_states[channel]['offset'] = offset
                return offset
            return None
            
        except Exception as e:
            logger.error(f"获取偏置失败: {e}")
            self.increment_error()
            return None
    
    def get_phase(self, channel: int = 1) -> Optional[float]:
        """获取相位
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            相位（度）
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        try:
            response = self.scpi.query(f':SOUR{channel}:PHAS?')
            if response:
                phase = float(response)
                self._channel_states[channel]['phase'] = phase
                return phase
            return None
            
        except Exception as e:
            logger.error(f"获取相位失败: {e}")
            self.increment_error()
            return None
    
    def get_waveform(self, channel: int = 1) -> Optional[str]:
        """获取波形类型
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            波形类型
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        try:
            response = self.scpi.query(f':SOUR{channel}:FUNC?')
            if response:
                waveform = response.strip().strip('"')
                self._channel_states[channel]['waveform'] = waveform
                return waveform
            return None
            
        except Exception as e:
            logger.error(f"获取波形类型失败: {e}")
            self.increment_error()
            return None
    
    def get_output_status(self, channel: int = 1) -> Optional[bool]:
        """获取输出状态
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            输出状态（True=打开，False=关闭）
        """
        if not self.is_connected:
            raise ConnectionError("波形发生器未连接")
        
        try:
            response = self.scpi.query(f':OUTP{channel}?')
            if response:
                status = response.strip() == '1'
                self._channel_states[channel]['output_enabled'] = status
                return status
            return None
            
        except Exception as e:
            logger.error(f"获取输出状态失败: {e}")
            self.increment_error()
            return None
    
    def read_status(self, channel: int = 1) -> Dict[str, Any]:
        """读取通道状态
        
        Args:
            channel: 通道号（1或2）
            
        Returns:
            通道状态字典
        """
        try:
            waveform = self.get_waveform(channel)
            frequency = self.get_frequency(channel)
            amplitude = self.get_amplitude(channel)
            offset = self.get_offset(channel)
            phase = self.get_phase(channel)
            output_status = self.get_output_status(channel)
            
            return {
                'channel': channel,
                'waveform': waveform,
                'frequency': frequency,
                'amplitude': amplitude,
                'offset': offset,
                'phase': phase,
                'output_enabled': output_status
            }
        except Exception as e:
            logger.error(f"读取通道状态失败: {e}")
            return {'channel': channel, 'error': str(e)}
    
    def read_data(self) -> Dict[str, Any]:
        """读取双通道完整数据
        
        Returns:
            双通道数据字典
        """
        ch1 = self.read_status(1)
        ch2 = self.read_status(2)
        return {'ch1': ch1, 'ch2': ch2}
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据
        
        Args:
            data: 数据字典
            
        Returns:
            是否成功
        """
        try:
            channel = data.get('channel', 1)
            waveform = data.get('waveform')
            frequency = data.get('frequency')
            amplitude = data.get('amplitude')
            offset = data.get('offset')
            phase = data.get('phase')
            output = data.get('output')
            
            if waveform is not None:
                self.set_waveform(waveform, 
                                frequency=frequency or self._channel_states[channel]['frequency'],
                                amplitude=amplitude or self._channel_states[channel]['amplitude'],
                                offset=offset or self._channel_states[channel]['offset'],
                                phase=phase or self._channel_states[channel]['phase'],
                                channel=channel)
            else:
                if frequency is not None:
                    self.set_frequency(frequency, channel)
                if amplitude is not None:
                    self.set_amplitude(amplitude, channel)
                if offset is not None:
                    self.set_offset(offset, channel)
                if phase is not None:
                    self.set_phase(phase, channel)
            
            if output is not None:
                if output:
                    self.output_on(channel)
                else:
                    self.output_off(channel)
            
            return True
            
        except Exception as e:
            logger.error(f"写入数据失败: {e}")
            return False
    
    def reset(self):
        """重置设备
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 重置所有状态
        - 集成平台设备重置
        """
        logger.info(f"重置波形发生器: {self.driver_id}")
        
        # 关闭所有输出
        for channel in [1, 2]:
            try:
                self.output_off(channel)
            except Exception as e:
                logger.warning(f"关闭通道{channel}输出失败: {e}")
        
        # 重置设备
        try:
            self.scpi.reset()
            time.sleep(1.0)
        except Exception as e:
            logger.warning(f"SCPI重置失败: {e}")
        
        # 重置状态
        self._channel_states = {
            1: {
                'waveform': self.WAVEFORM_SIN,
                'frequency': 1000.0,
                'amplitude': 1.0,
                'offset': 0.0,
                'phase': 0.0,
                'output_enabled': False
            },
            2: {
                'waveform': self.WAVEFORM_SIN,
                'frequency': 1000.0,
                'amplitude': 1.0,
                'offset': 0.0,
                'phase': 0.0,
                'output_enabled': False
            }
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
        
        logger.info(f"波形发生器重置完成: {self.driver_id}")
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查
        
        【架构集成】
        - 继承基类健康检查
        - 添加波形发生器特定检查
        - 集成平台设备状态
        - 提供详细诊断信息
        
        Returns:
            健康状态字典
        """
        base = super().health_check()
        
        # 波形发生器特定健康检查
        try:
            if self.is_connected:
                # 读取双通道状态
                ch1_status = self.read_status(1)
                ch2_status = self.read_status(2)
                
                # 获取设备错误
                device_error = self.scpi.get_error()
                
                # 更新平台设备心跳
                if self.platform_device:
                    self.platform_device.update_heartbeat()
                
                generator_health = {
                    'device_type': 'waveform_generator',
                    'manufacturer': self._device_info['manufacturer'],
                    'model': self._device_info['model'],
                    'channels': self._device_info['channels'],
                    'channel_states': self._channel_states,
                    'real_time_status': {
                        'ch1': ch1_status,
                        'ch2': ch2_status
                    },
                    'device_error': device_error,
                    'protocol_driver_id': self.scpi.driver_id if self.scpi else None,
                    'platform_device_id': self.platform_device.id if self.platform_device else None,
                    'platform_device_connected': self.platform_device.is_connected if self.platform_device else False
                }
            else:
                generator_health = {
                    'device_type': 'waveform_generator',
                    'manufacturer': self._device_info['manufacturer'],
                    'model': self._device_info['model'],
                    'channels': self._device_info['channels'],
                    'channel_states': self._channel_states,
                    'status': 'disconnected',
                    'protocol_driver_id': self.scpi.driver_id if self.scpi else None,
                    'platform_device_id': self.platform_device.id if self.platform_device else None,
                    'platform_device_connected': False
                }
        except Exception as e:
            logger.error(f"健康检查异常: {e}")
            generator_health = {
                'device_type': 'waveform_generator',
                'status': 'error',
                'error': str(e),
                'protocol_driver_id': self.scpi.driver_id if self.scpi else None,
                'platform_device_id': self.platform_device.id if self.platform_device else None
            }
        
        base.update(generator_health)
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