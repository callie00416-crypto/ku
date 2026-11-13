"""ASDB2电机驱动（符合新框架）"""
import time
import logging
from typing import Dict, Any, Optional
from shared.drivers.base.base_device import BaseDevice

logger = logging.getLogger(__name__)


class ASDB2Driver(BaseDevice):
    """台达ASDA-B2系列伺服驱动器驱动（符合新框架）
    
    【组合关系】
    ASDB2Driver -> ModbusDriver -> RS485Comm
    
    【架构集成】
    - 继承 BaseDevice 基类
    - 支持平台设备生命周期管理
    - 集成平台事件系统
    - 符合工业设备规范
    
    【设备信息】
    - 厂商：台达（DELTA）
    - 型号：ASDA-B2
    - 通讯：MODBUS-RTU
    - 速度范围：0-3000 RPM
    """
    
    # 速度源映射
    SPEED_SOURCE_P1_09 = 'P1-09'
    SPEED_SOURCE_P1_10 = 'P1-10'
    SPEED_SOURCE_P1_11 = 'P1-11'
    
    # 方向定义
    DIRECTION_CW = 'CW'      # 顺时针
    DIRECTION_CCW = 'CCW'    # 逆时针
    
    # 速度范围
    MIN_SPEED = 0.0          # 0 RPM
    MAX_SPEED = 3000.0       # 3000 RPM
    
    def __init__(self, driver_id: str = 'asdb2', protocol=None, 
                 platform_device=None, **kwargs):
        """
        Args:
            driver_id: 驱动ID
            protocol: 协议对象（ModbusDriver）
            platform_device: 平台设备对象（可选）
            **kwargs: 其他参数
        """
        super().__init__(driver_id, protocol, **kwargs)
        self.modbus = protocol
        self.platform_device = platform_device
        
        # 设备参数
        self.slave_id = kwargs.get('slave_id', 0x7F)
        
        # 电机状态
        self._motor_state = {
            'speed_rpm': 0.0,
            'direction': self.DIRECTION_CW,
            'speed_source': self.SPEED_SOURCE_P1_11,
            'servo_enabled': False,
            'feedback_speed': 0.0
        }
        
        # 设备信息
        self._device_info = {
            'manufacturer': 'DELTA',
            'model': 'ASDA-B2',
            'protocol': 'MODBUS-RTU',
            'max_speed': 3000.0,
            'channels': 1
        }
    
    def calc_addr(self, pxx, yy):
        """计算MODBUS地址
        
        Args:
            pxx: 参数组号
            yy: 参数号
            
        Returns:
            MODBUS地址
        """
        return pxx * 256 + yy * 2
    
    def connect(self) -> bool:
        """连接电机驱动器
        
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
            
            # 更新状态为已连接
            self._is_connected = True
            self._device_status = "connected"
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.connect()
            
            logger.info(f"ASDB2电机驱动器连接成功: {self.driver_id}")
            return True
        except Exception as e:
            logger.error(f"ASDB2电机驱动器连接失败: {e}")
            self._device_status = "fault"
            self.increment_error()
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.disconnect()
            
            return False
    
    def disconnect(self):
        """断开电机驱动器连接
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        # 停止电机
        try:
            self.stop_motor()
        except Exception as e:
            logger.warning(f"停止电机失败: {e}")
        
        # 关闭伺服
        try:
            self.enable_servo(False)
        except Exception as e:
            logger.warning(f"关闭伺服失败: {e}")
        
        self._is_connected = False
        self._device_status = "disconnected"
        
        # 断开协议层
        if self.modbus:
            self.modbus.disconnect()
        
        # 集成平台设备
        if self.platform_device:
            self.platform_device.disconnect()
        
        # 更新状态
        self._motor_state['servo_enabled'] = False
        self._motor_state['speed_rpm'] = 0.0
        
        logger.info(f"ASDB2电机驱动器已断开: {self.driver_id}")
    
    def read_data(self) -> Dict[str, Any]:
        """读取电机驱动器数据
        
        Returns:
            电机状态数据
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        try:
            feedback_speed = self.read_feedback_speed()
            
            data = {
                'driver_id': self.driver_id,
                'speed_rpm': self._motor_state['speed_rpm'],
                'direction': self._motor_state['direction'],
                'speed_source': self._motor_state['speed_source'],
                'servo_enabled': self._motor_state['servo_enabled'],
                'feedback_speed': feedback_speed,
                'timestamp': time.time()
            }
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return data
            
        except Exception as e:
            logger.error(f"读取电机数据失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return {}
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入电机驱动器数据
        
        Args:
            data: 要写入的数据
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        try:
            # 设置速度
            if 'speed_rpm' in data:
                self.set_speed(data['speed_rpm'])
            
            # 设置方向
            if 'direction' in data:
                self.set_direction(data['direction'])
            
            # 设置速度源
            if 'speed_source' in data:
                self.select_speed_source(data['speed_source'])
            
            # 使能伺服
            if 'servo_enabled' in data:
                self.enable_servo(data['servo_enabled'])
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return True
            
        except Exception as e:
            logger.error(f"写入电机数据失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def reset(self):
        """重置电机驱动器"""
        try:
            self.stop_motor()
            self.enable_servo(False)
            self.reset_error()
            logger.info(f"电机驱动器已重置: {self.driver_id}")
        except Exception as e:
            logger.error(f"重置电机驱动器失败: {e}")
            self.increment_error()
    
    def read_feedback_speed(self) -> Optional[float]:
        """读取反馈速度（单位：RPM）
        
        Returns:
            反馈速度（负值=顺时针，正值=逆时针）
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        try:
            # 设置P0-02=6（显示电机转速）
            self.modbus.write_register(address=self.calc_addr(0, 2), value=6, slave_id=self.slave_id)
            time.sleep(0.05)
            
            # 读取P0-09（32位有符号整数，单位0.1 r/min）
            r = self.modbus.read_registers(address=self.calc_addr(0, 9), count=2, slave_id=self.slave_id)
            if r and len(r) >= 2:
                low_word = r[0]
                high_word = r[1]
                speed_value = (high_word << 16) | low_word
                
                # 处理32位有符号整数
                if speed_value & 0x80000000:
                    speed_value = speed_value - 0x100000000
                
                # 转换为RPM（单位0.1 r/min）
                speed_rpm = speed_value / 10.0
                
                self._motor_state['feedback_speed'] = speed_rpm
                
                # 集成平台设备操作记录
                if self.platform_device:
                    self.platform_device.record_operation(success=True)
                
                return speed_rpm
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return None
            
        except Exception as e:
            logger.error(f"读取反馈速度失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return None
    
    def set_speed(self, p1_09=None, p1_10=None, p1_11=None) -> bool:
        """设置速度值（单位：RPM）
        
        Args:
            p1_09: P1-09速度值
            p1_10: P1-10速度值
            p1_11: P1-11速度值
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        try:
            if p1_09 is not None:
                if p1_09 < self.MIN_SPEED or p1_09 > self.MAX_SPEED:
                    raise ValueError(f"P1-09速度超出范围: {self.MIN_SPEED}-{self.MAX_SPEED}RPM")
                value = int(p1_09 * 10)
                self.modbus.write_registers(address=self.calc_addr(1, 9), values=[value & 0xFFFF, (value >> 16) & 0xFFFF], slave_id=self.slave_id)
                time.sleep(0.1)
            
            if p1_10 is not None:
                if p1_10 < self.MIN_SPEED or p1_10 > self.MAX_SPEED:
                    raise ValueError(f"P1-10速度超出范围: {self.MIN_SPEED}-{self.MAX_SPEED}RPM")
                value = int(p1_10 * 10)
                self.modbus.write_registers(address=self.calc_addr(1, 10), values=[value & 0xFFFF, (value >> 16) & 0xFFFF], slave_id=self.slave_id)
                time.sleep(0.1)
            
            if p1_11 is not None:
                if p1_11 < self.MIN_SPEED or p1_11 > self.MAX_SPEED:
                    raise ValueError(f"P1-11速度超出范围: {self.MIN_SPEED}-{self.MAX_SPEED}RPM")
                value = int(p1_11 * 10)
                self.modbus.write_registers(address=self.calc_addr(1, 11), values=[value & 0xFFFF, (value >> 16) & 0xFFFF], slave_id=self.slave_id)
                time.sleep(0.1)
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return True
            
        except Exception as e:
            logger.error(f"设置速度失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def select_speed_source(self, source) -> bool:
        """选择速度源
        
        Args:
            source: 'P1-09', 'P1-10', 'P1-11'
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        if source not in [self.SPEED_SOURCE_P1_09, self.SPEED_SOURCE_P1_10, self.SPEED_SOURCE_P1_11]:
            raise ValueError(f"无效速度源: {source}")
        
        try:
            # 根据source确定reg值
            # reg=1 → P1-09, reg=2 → P1-10, reg=3 → P1-11
            reg = 1 if source == self.SPEED_SOURCE_P1_09 else \
                  2 if source == self.SPEED_SOURCE_P1_10 else 3
            
            # 初始化SPD0和SPD1
            spd0 = 0x0014
            spd1 = 0x0015
            
            # 根据reg值设置SPD0和SPD1
            # reg=1 (01): SPD0=OFF, SPD1=ON
            # reg=2 (10): SPD0=ON, SPD1=OFF
            # reg=3 (11): SPD0=OFF, SPD1=OFF
            if reg == 1:
                spd1 |= 0x0100  # SPD1 ON
            elif reg == 2:
                spd0 |= 0x0100  # SPD0 ON
            elif reg == 3:
                pass  # SPD0 OFF, SPD1 OFF
            
            self.modbus.write_register(address=0x0218, value=spd0, slave_id=self.slave_id)
            time.sleep(0.1)
            
            self.modbus.write_register(address=0x021A, value=spd1, slave_id=self.slave_id)
            time.sleep(0.1)
            
            self._motor_state['speed_source'] = source
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return True
            
        except Exception as e:
            logger.error(f"选择速度源失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def set_direction(self, direction) -> bool:
        """设置方向
        
        Args:
            direction: 'CW'（顺时针）或'CCW'（逆时针）
            注意：CMDINV=0x0006是顺时针，CMDINV=0x0106是逆时针
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        if direction not in [self.DIRECTION_CW, self.DIRECTION_CCW]:
            raise ValueError(f"无效方向: {direction}")
        
        try:
            cmdinv = 0x0006 if direction == self.DIRECTION_CW else 0x0106
            self.modbus.write_register(address=0x021E, value=cmdinv, slave_id=self.slave_id)
            time.sleep(0.1)
            
            self._motor_state['direction'] = direction
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return True
            
        except Exception as e:
            logger.error(f"设置方向失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def initialize_driver(self) -> bool:
        """初始化电机驱动器
        
        参考103Calibrator的startDriver函数，执行必要的初始化步骤：
        1. 禁用EEPROM（P2-30=5）
        2. 配置DI7为速度模式（P2-16=0x0118）
        
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        try:
            # 1. 禁用EEPROM（P2-30=5）
            self.modbus.write_register(address=0x023C, value=5, slave_id=self.slave_id)
            time.sleep(0.1)
            
            # 2. 配置DI7为速度模式（P2-16=0x0118）
            self.modbus.write_register(address=0x0220, value=0x0118, slave_id=self.slave_id)
            time.sleep(0.1)
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info("电机驱动器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化电机驱动器失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def enable_servo(self, enable=True) -> bool:
        """使能/关闭伺服
        
        Args:
            enable: True=使能，False=关闭
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        try:
            if enable:
                # 使能前先将速度清零，避免驱动器使能后立即转动
                self.set_speed(p1_09=0, p1_10=0, p1_11=0)
                
            # 103Calibrator中：DriverOn → 0x0001, DriverOff → 0x0101
            status = 0x0001 if enable else 0x0101
            self.modbus.write_register(address=0x0214, value=status, slave_id=self.slave_id)
            time.sleep(0.2)
            
            self._motor_state['servo_enabled'] = enable
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"伺服{'使能' if enable else '关闭'}")
            return True
            
        except Exception as e:
            logger.error(f"使能伺服失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def run_motor(self, speed_rpm, direction='CW', source='P1-11') -> bool:
        """运行电机
        
        Args:
            speed_rpm: 速度（RPM）
            direction: 方向（'CW'或'CCW'）
            source: 速度源（'P1-09', 'P1-10', 'P1-11'）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        try:
            # 设置速度
            self.set_speed(**{source.lower().replace('-', '_'): speed_rpm})
            
            # 选择速度源
            self.select_speed_source(source)
            
            # 设置方向
            self.set_direction(direction)
            
            self._motor_state['speed_rpm'] = speed_rpm
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info(f"电机运行: {speed_rpm} RPM, {direction}, {source}")
            return True
            
        except Exception as e:
            logger.error(f"运行电机失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            
            return False
    
    def stop_motor(self) -> bool:
        """停止电机（设置速度为0）
        
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")
        
        try:
            self.set_speed(p1_09=0, p1_10=0, p1_11=0)
            self._motor_state['speed_rpm'] = 0.0
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            logger.info("电机已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止电机失败: {e}")
            self.increment_error()
            
            # 集成平台设备操作记录
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
    def motor_state(self) -> Dict[str, Any]:
        """获取电机状态"""
        return self._motor_state.copy()
    
    @property
    def device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        return self._device_info.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        base = super().health_check()
        base.update({
            'device_type': 'asdb2',
            'motor_state': self._motor_state,
            'device_info': self._device_info,
        })
        return base