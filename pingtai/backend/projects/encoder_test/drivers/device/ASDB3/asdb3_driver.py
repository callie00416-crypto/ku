"""ASDB3电机驱动（符合新框架）"""
import time
import logging
from typing import Dict, Any, Optional
from shared.drivers.base.base_device import BaseDevice

logger = logging.getLogger(__name__)


class ASDB3Driver(BaseDevice):
    """台达ASDA-B3系列伺服驱动器驱动（符合新框架）

    【组合关系】
    ASDB3Driver -> ModbusDriver -> RS485Comm

    【架构集成】
    - 继承 BaseDevice 基类
    - 支持平台设备生命周期管理
    - 集成平台事件系统
    - 符合工业设备规范

    【设备信息】
    - 厂商：台达（DELTA）
    - 型号：ASDA-B3
    - 通讯：MODBUS-RTU / CANopen / EtherCAT
    - 速度范围：0-6000 RPM
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
    MAX_SPEED = 6000.0       # 6000 RPM

    # 控制模式
    CONTROL_MODE_SPEED = 'S'      # 速度模式
    CONTROL_MODE_TORQUE = 'T'     # 转矩模式
    CONTROL_MODE_POSITION = 'Pt'  # 位置模式
    CONTROL_MODE_PR = 'Pr'        # PR模式

    # PR命令类型
    PR_CMD_STOP = 0x00         # 停止
    PR_CMD_SPEED = 0x01        # 速度命令
    PR_CMD_SINGLE = 0x02       # 定位控制（单次）
    PR_CMD_AUTO = 0x03         # 定位控制（自动）
    PR_CMD_JUMP = 0x07         # 跳转命令
    PR_CMD_WRITE = 0x08        # 写入命令
    PR_CMD_INDEX = 0x0A        # 旋转轴位置命令

    # PR命令选项 (P6.002 Y字段 bit定义)
    PR_OPT_INS = 0x01          # bit0: 中断前一路径
    PR_OPT_OVLP = 0x04         # bit2: 重叠/相对定位(REL)
    PR_OPT_CMD = 0x08          # bit3: 增量定位(INC)/方向

    # PR位置命令类型 (OPT字段 bit3:bit2)
    PR_POS_TYPE_ABS = 0x00     # 00: 绝对定位
    PR_POS_TYPE_REL = 0x04     # 01: 相对定位
    PR_POS_TYPE_INC = 0x08     # 10: 增量定位
    PR_POS_TYPE_CAP = 0x0C     # 11: 高速位置捕获

    # PR位置命令类型
    PR_POS_ABS = 'ABS'         # 绝对定位
    PR_POS_REL = 'REL'         # 相对定位
    PR_POS_INC = 'INC'         # 增量定位
    PR_POS_CAP = 'CAP'         # 高速位置捕获

    def __init__(self, driver_id: str = 'asdb3', protocol=None,
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
            'model': 'ASDA-B3',
            'protocol': 'MODBUS-RTU',
            'max_speed': 6000.0,
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

        【ASDB3特殊】
        - 连接后必须设置P3-006=0x1FFF开通通讯控制权
        - 否则无法通过Modbus控制DI/DO
        """
        try:
            self._device_status = "connecting"

            if not self.modbus.connect():
                self._device_status = "fault"
                if self.platform_device:
                    self.platform_device.disconnect()
                return False

            self._is_connected = True
            self._device_status = "connected"

            # ASDB3: 开通通讯控制权 (P3-006=0x1FFF)
            self._enable_comm_control()

            if self.platform_device:
                self.platform_device.connect()

            logger.info(f"ASDB3电机驱动器连接成功: {self.driver_id}")
            return True
        except Exception as e:
            logger.error(f"ASDB3电机驱动器连接失败: {e}")
            self._device_status = "fault"
            self.increment_error()

            if self.platform_device:
                self.platform_device.disconnect()

            return False

    def _enable_comm_control(self) -> bool:
        """开通通讯控制权

        ASDB3必须设置P3-006=0x1FFF才能通过Modbus控制所有I/O点。
        如果不设置，DI/DO控制命令将被忽略。

        Returns:
            是否成功
        """
        try:
            addr = self.calc_addr(3, 6)
            current = self.modbus.read_register(address=addr, slave_id=self.slave_id)
            if current == 0x1FFF:
                logger.info("通讯控制权已开通")
                return True

            self.modbus.write_register(address=addr, value=0x1FFF, slave_id=self.slave_id)
            time.sleep(0.1)

            verify = self.modbus.read_register(address=addr, slave_id=self.slave_id)
            if verify == 0x1FFF:
                logger.info("通讯控制权开通成功 (P3-006=0x1FFF)")
                return True
            else:
                logger.warning(f"通讯控制权开通可能失败，P3-006=0x{verify:04X}")
                return False
        except Exception as e:
            logger.error(f"开通通讯控制权失败: {e}")
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

        logger.info(f"ASDB3电机驱动器已断开: {self.driver_id}")

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

    def read_e_gear_ratio(self) -> Dict[str, int]:
        """读取电子齿轮比

        ASDB3电子齿轮比: PUU = f1, 编码器脉冲 = f2
        f2 = f1 × N / M
        每转PUU数 = M (当N=编码器分辨率时)

        P1.044 = N (分子), 默认16777216
        P1.045 = M (分母), 默认100000

        Returns:
            {'numerator': N, 'denominator': M, 'puu_per_rev': M}
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        try:
            n_regs = self.modbus.read_registers(
                address=self.calc_addr(1, 44), count=2, slave_id=self.slave_id
            )
            m_regs = self.modbus.read_registers(
                address=self.calc_addr(1, 45), count=2, slave_id=self.slave_id
            )

            n = self._read_32bit_signed(n_regs) if n_regs else 16777216
            m = self._read_32bit_signed(m_regs) if m_regs else 100000

            return {'numerator': n, 'denominator': m, 'puu_per_rev': m}

        except Exception as e:
            logger.error(f"读取电子齿轮比失败: {e}")
            return {'numerator': 16777216, 'denominator': 100000, 'puu_per_rev': 100000}

    def read_feedback_speed(self) -> Optional[float]:
        """读取反馈速度（单位：RPM）

        ASDB3监控变量读取方式：
        1. 写监控代码到P0.017（选择监控寄存器1的内容）
        2. 读P0.009（32位，获取监控寄存器1的值）

        监控代码7 = 速度反馈，单位0.1 rpm

        Returns:
            反馈速度（负值=顺时针，正值=逆时针）
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        try:
            self.modbus.write_register(address=self.calc_addr(0, 17), value=7, slave_id=self.slave_id)
            time.sleep(0.05)

            r = self.modbus.read_registers(address=self.calc_addr(0, 9), count=2, slave_id=self.slave_id)
            if r and len(r) >= 2:
                low_word = r[0]
                high_word = r[1]
                speed_value = (high_word << 16) | low_word

                if speed_value & 0x80000000:
                    speed_value = speed_value - 0x100000000

                speed_rpm = speed_value / 10.0

                self._motor_state['feedback_speed'] = speed_rpm

                if self.platform_device:
                    self.platform_device.record_operation(success=True)

                return speed_rpm

            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return None

        except Exception as e:
            logger.error(f"读取反馈速度失败: {e}")
            self.increment_error()

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

        执行必要的初始化步骤：
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

        ASDB3使用P4-007控制DI状态位来使能伺服：
        - bit0 = SON (伺服使能)
        - 需要先开通P3-006通讯控制权

        同时也写入0x0214以兼容ASDB2方式。

        Args:
            enable: True=使能，False=关闭

        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        try:
            if enable:
                self.set_speed(p1_09=0, p1_10=0, p1_11=0)

            # ASDB3方式: 通过P4-007控制DI状态
            addr_p4_007 = self.calc_addr(4, 7)
            current_di = self.modbus.read_register(address=addr_p4_007, slave_id=self.slave_id)
            if current_di is None:
                current_di = 0

            if enable:
                new_di = current_di | 0x0001  # bit0=SON
            else:
                new_di = current_di & ~0x0001  # 清除SON

            self.modbus.write_register(address=addr_p4_007, value=new_di, slave_id=self.slave_id)
            time.sleep(0.1)

            # ASDB2兼容方式: 写入0x0214
            status = 0x0001 if enable else 0x0101
            self.modbus.write_register(address=0x0214, value=status, slave_id=self.slave_id)
            time.sleep(0.2)

            self._motor_state['servo_enabled'] = enable

            if self.platform_device:
                self.platform_device.record_operation(success=True)

            logger.info(f"伺服{'使能' if enable else '关闭'}")
            return True

        except Exception as e:
            logger.error(f"使能伺服失败: {e}")
            self.increment_error()

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
            'device_type': 'asdb3',
            'motor_state': self._motor_state,
            'device_info': self._device_info,
        })
        return base

    def set_control_mode(self, mode: str) -> bool:
        """设置控制模式

        Args:
            mode: 'S'（速度）、'T'（转矩）、'Pt'（位置）、'Pr'（PR模式）

        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        mode_map = {
            self.CONTROL_MODE_SPEED: 0,
            self.CONTROL_MODE_TORQUE: 1,
            self.CONTROL_MODE_POSITION: 2,
            self.CONTROL_MODE_PR: 3
        }

        if mode not in mode_map:
            raise ValueError(f"无效控制模式: {mode}")

        try:
            # 设置P1-001为对应模式
            self.modbus.write_register(address=self.calc_addr(1, 1), value=mode_map[mode], slave_id=self.slave_id)
            time.sleep(0.1)

            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)

            logger.info(f"控制模式已设置为: {mode}")
            return True

        except Exception as e:
            logger.error(f"设置控制模式失败: {e}")
            self.increment_error()

            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return False

    def set_pr_path(self, pr_number: int, command_type: int, data: int = 0,
                    acc_index: int = 0, dec_index: int = 0, dly_index: int = 0,
                    spd_index: int = 0, options: int = 0, auto_next: bool = False) -> bool:
        """设置PR路径

        根据ASDB3手册，P6.002属性格式（32位HEX）：
            High word              Low word
            D      C      B      A      U      Z      Y      X
            DEC    AUTO   DLY    SPD    ACC    -      OPT    TYPE

            X (bit 3-0):   TYPE  - 命令类型 (1=速度, 2=单次定位, 3=自动定位, 7=跳转, 8=写入, A=旋转轴)
            Y (bit 7-4):   OPT   - 选项 (bit0=INS中断, bit1=AUTO自动, bit2=CMD, bit3=DIR/OVLP)
            Z (bit 11-8):  ACC   - 加速时间索引 (0-F, 对应P5.020-P5.035)
            U (bit 15-12): DEC   - 减速时间索引 (0-F, 对应P5.020-P5.035)
            A (bit 19-16): SPD   - 速度索引 (0-F, 对应P5.060-P5.075)
            B (bit 23-20): DLY   - 延迟时间索引 (0-F, 对应P5.040-P5.055)
            C (bit 27-24): AUTO  - 自动执行 (仅TYPE=A时有效, bit2=1自动)
            D (bit 31-28): 保留

        Args:
            pr_number: PR编号（0-99）
            command_type: 命令类型
            data: 命令数据（32位）
            acc_index: 加速时间索引（0-15）
            dec_index: 减速时间索引（0-15）
            dly_index: 延迟时间索引（0-15）
            spd_index: 速度索引（0-15）
            options: 选项位（INS=0x01, AUTO=0x02, CMD=0x04, OVLP=0x08）
            auto_next: 自动执行（仅TYPE=A时有效）

        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        if pr_number < 0 or pr_number > 99:
            raise ValueError(f"PR编号超出范围: 0-99")

        try:
            property_value = 0
            property_value |= (command_type & 0x0F) << 0    # X: TYPE
            property_value |= (options & 0x0F) << 4         # Y: OPT
            property_value |= (acc_index & 0x0F) << 8       # Z: ACC
            property_value |= (dec_index & 0x0F) << 12      # U: DEC
            property_value |= (spd_index & 0x0F) << 16      # A: SPD
            property_value |= (dly_index & 0x0F) << 20      # B: DLY
            if auto_next:
                property_value |= (1 << 26)                  # C: AUTO bit2

            if pr_number < 50:
                property_addr = self.calc_addr(6, pr_number * 2)
                data_addr = self.calc_addr(6, pr_number * 2 + 1)
            else:
                property_addr = self.calc_addr(7, (pr_number - 50) * 2)
                data_addr = self.calc_addr(7, (pr_number - 50) * 2 + 1)

            low_word = property_value & 0xFFFF
            high_word = (property_value >> 16) & 0xFFFF
            self.modbus.write_registers(address=property_addr, values=[low_word, high_word], slave_id=self.slave_id)
            time.sleep(0.05)

            low_word = data & 0xFFFF
            high_word = (data >> 16) & 0xFFFF
            self.modbus.write_registers(address=data_addr, values=[low_word, high_word], slave_id=self.slave_id)
            time.sleep(0.05)

            if self.platform_device:
                self.platform_device.record_operation(success=True)

            logger.info(f"PR#{pr_number:02d}已设置: 类型=0x{command_type:02X}, 数据={data}, 属性=0x{property_value:08X}")
            return True

        except Exception as e:
            logger.error(f"设置PR路径失败: {e}")
            self.increment_error()

            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return False

    def set_pr_speed_command(self, pr_number: int, speed_rpm: float,
                             acc_index: int = 0, dec_index: int = 0,
                             dly_index: int = 0, spd_index: int = 0,
                             interrupt: bool = False) -> bool:
        """设置PR速度命令

        Args:
            pr_number: PR编号（0-99）
            speed_rpm: 目标速度（RPM）
            acc_index: 加速时间索引（0-15）
            dec_index: 减速时间索引（0-15）
            dly_index: 延迟时间索引（0-15）
            spd_index: 速度索引（0-15）
            interrupt: 是否中断

        Returns:
            是否成功
        """
        options = self.PR_OPT_INS if interrupt else 0
        data = int(speed_rpm * 10)  # 转换为0.1 RPM

        return self.set_pr_path(
            pr_number=pr_number,
            command_type=self.PR_CMD_SPEED,
            data=data,
            acc_index=acc_index,
            dec_index=dec_index,
            dly_index=dly_index,
            spd_index=spd_index,
            options=options
        )

    def set_pr_position_command(self, pr_number: int, position_puu: int,
                                pos_type: str = 'ABS',
                                acc_index: int = 0, dec_index: int = 0,
                                dly_index: int = 0, spd_index: int = 0,
                                interrupt: bool = False, overlap: bool = False,
                                auto_next: bool = False) -> bool:
        """设置PR位置命令

        根据ASDB3手册Table 7.1.3.3.1，位置命令OPT字段(bit3:bit2)：
        - 00: ABS (绝对定位)
        - 01: REL (相对定位)
        - 10: INC (增量定位)
        - 11: CAP (高速位置捕获)

        TYPE字段：
        - 0x02: SINGLE - 单次定位，执行完毕后停止
        - 0x03: AUTO - 自动定位，执行完毕后自动加载下一个PR路径

        Args:
            pr_number: PR编号（0-99）
            position_puu: 目标位置（PUU）
            pos_type: 位置类型（'ABS'=绝对, 'REL'=相对, 'INC'=增量, 'CAP'=捕获）
            acc_index: 加速时间索引（0-15）
            dec_index: 减速时间索引（0-15）
            dly_index: 延迟时间索引（0-15）
            spd_index: 速度索引（0-15）
            interrupt: 是否中断前一路径
            overlap: 是否重叠（允许下一个路径重叠）
            auto_next: 是否自动执行下一个PR

        Returns:
            是否成功
        """
        pos_type_map = {
            'ABS': self.PR_POS_TYPE_ABS,
            'REL': self.PR_POS_TYPE_REL,
            'INC': self.PR_POS_TYPE_INC,
            'CAP': self.PR_POS_TYPE_CAP,
        }

        options = pos_type_map.get(pos_type, self.PR_POS_TYPE_ABS)
        if interrupt:
            options |= self.PR_OPT_INS
        if overlap:
            options |= self.PR_OPT_OVLP

        command_type = self.PR_CMD_AUTO if auto_next else self.PR_CMD_SINGLE

        return self.set_pr_path(
            pr_number=pr_number,
            command_type=command_type,
            data=position_puu,
            acc_index=acc_index,
            dec_index=dec_index,
            dly_index=dly_index,
            spd_index=spd_index,
            options=options
        )

    def set_pr_jump_command(self, pr_number: int, target_pr: int,
                           dly_index: int = 0, interrupt: bool = False) -> bool:
        """设置PR跳转命令

        Args:
            pr_number: PR编号（0-99）
            target_pr: 目标PR编号（0-99）
            dly_index: 延迟时间索引（0-15）
            interrupt: 是否中断

        Returns:
            是否成功
        """
        if target_pr < 0 or target_pr > 99:
            raise ValueError(f"目标PR编号超出范围: 0-99")

        options = self.PR_OPT_INS if interrupt else 0

        return self.set_pr_path(
            pr_number=pr_number,
            command_type=self.PR_CMD_JUMP,
            data=target_pr,
            dly_index=dly_index,
            options=options
        )

    def set_pr_write_command(self, pr_number: int, dest_param: str,
                            source_value: int, source_type: str = 'constant',
                            dly_index: int = 0, interrupt: bool = False,
                            write_to_eeprom: bool = False) -> bool:
        """设置PR写入命令

        Args:
            pr_number: PR编号（0-99）
            dest_param: 目标参数（如'P1.001'）
            source_value: 源值
            source_type: 源类型（'constant'=常量, 'parameter'=参数, 'data_array'=数据数组）
            dly_index: 延迟时间索引（0-15）
            interrupt: 是否中断
            write_to_eeprom: 是否写入EEPROM

        Returns:
            是否成功
        """
        options = 0
        if interrupt:
            options |= self.PR_OPT_INS
        if write_to_eeprom:
            options |= self.PR_OPT_ROM

        # 解析目标参数
        try:
            parts = dest_param.upper().replace('P', '').split('.')
            param_group = int(parts[0])
            param_number = int(parts[1])
        except:
            raise ValueError(f"无效参数格式: {dest_param}")

        # 构造数据值（包含源类型和目标参数）
        data = 0
        data |= (source_value & 0xFFFF) << 16
        data |= (param_number & 0xFF) << 8
        data |= param_group & 0xFF

        return self.set_pr_path(
            pr_number=pr_number,
            command_type=self.PR_CMD_WRITE,
            data=data,
            dly_index=dly_index,
            options=options
        )

    def set_pr_shared_params(self, param_type: str, index: int, value: float) -> bool:
        """设置共享PR参数

        Args:
            param_type: 'ACC'（加减速）、'DLY'（延迟）、'SPD'（速度）
            index: 索引（0-15）
            value: 参数值

        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        if index < 0 or index > 15:
            raise ValueError(f"索引超出范围: 0-15")

        param_map = {
            'ACC': (5, 20),
            'DEC': (5, 20),
            'DLY': (5, 40),
            'SPD': (5, 60)
        }

        if param_type not in param_map:
            raise ValueError(f"无效参数类型: {param_type}")

        try:
            param_group, param_start = param_map[param_type]
            param_number = param_start + index
            address = self.calc_addr(param_group, param_number)

            if param_type in ['ACC', 'DEC']:
                int_value = int(value)
            elif param_type == 'DLY':
                int_value = int(value)
            else:  # SPD - 32位参数，单位0.1 RPM
                int_value = int(value * 10)

            if param_type == 'SPD':
                low_word = int_value & 0xFFFF
                high_word = (int_value >> 16) & 0xFFFF
                self.modbus.write_registers(address=address, values=[low_word, high_word], slave_id=self.slave_id)
            else:
                self.modbus.write_register(address=address, value=int_value, slave_id=self.slave_id)
            time.sleep(0.05)

            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)

            logger.info(f"共享参数已设置: {param_type}[{index}] = {value}")
            return True

        except Exception as e:
            logger.error(f"设置共享PR参数失败: {e}")
            self.increment_error()

            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return False

    def trigger_pr_command(self, pr_number: int) -> bool:
        """触发PR命令

        ASDB3使用P5-007触发PR命令（非DI信号方式）：
        - 写入1-99: 执行指定PR路径
        - 写入0: 执行回原点
        - 写入1000: 执行停止命令

        读取P5-007可获取执行状态：
        - 1-99: 正在执行
        - 10001-10099: 命令完成但电机未到位
        - 20001-20099: 命令完成且电机到位

        Args:
            pr_number: PR编号（0-99）

        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        if pr_number < 0 or pr_number > 99:
            raise ValueError(f"PR编号超出范围: 0-99")

        try:
            addr_p5_007 = self.calc_addr(5, 7)

            current = self.modbus.read_register(address=addr_p5_007, slave_id=self.slave_id)
            if current is not None and 1 <= (current % 10000) <= 99 and current < 10000:
                logger.warning(f"PR#{current}正在执行中，先停止")
                self.modbus.write_register(address=addr_p5_007, value=1000, slave_id=self.slave_id)
                time.sleep(0.2)

            self.modbus.write_register(address=addr_p5_007, value=pr_number, slave_id=self.slave_id)
            time.sleep(0.1)

            if self.platform_device:
                self.platform_device.record_operation(success=True)

            logger.info(f"PR命令已触发: PR#{pr_number:02d} (P5-007={pr_number})")
            return True

        except Exception as e:
            logger.error(f"触发PR命令失败: {e}")
            self.increment_error()

            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return False

    def stop_pr_command(self) -> bool:
        """停止PR命令

        通过P5-007=1000执行停止命令，等同于DI.STP。

        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        try:
            addr_p5_007 = self.calc_addr(5, 7)
            self.modbus.write_register(address=addr_p5_007, value=1000, slave_id=self.slave_id)
            time.sleep(0.1)

            if self.platform_device:
                self.platform_device.record_operation(success=True)

            logger.info("PR命令已停止 (P5-007=1000)")
            return True

        except Exception as e:
            logger.error(f"停止PR命令失败: {e}")
            self.increment_error()

            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return False

    def read_pr_status(self) -> Dict[str, Any]:
        """读取PR执行状态

        通过读取P5-007获取当前PR执行状态：
        - 0: 无命令
        - 1-99: 正在执行PR#1-99
        - 10001-10099: 命令完成但电机未到位(TPOS=Off)
        - 20001-20099: 命令完成且电机到位(TPOS=On)

        Returns:
            包含pr_number, executing, completed, positioned
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        try:
            addr_p5_007 = self.calc_addr(5, 7)
            value = self.modbus.read_register(address=addr_p5_007, slave_id=self.slave_id)

            if value is None:
                return {'pr_number': 0, 'executing': False, 'completed': False, 'positioned': False}

            if value >= 20000:
                pr_num = value - 20000
                return {'pr_number': pr_num, 'executing': False, 'completed': True, 'positioned': True, 'raw': value}
            elif value >= 10000:
                pr_num = value - 10000
                return {'pr_number': pr_num, 'executing': False, 'completed': True, 'positioned': False, 'raw': value}
            elif 1 <= value <= 99:
                return {'pr_number': value, 'executing': True, 'completed': False, 'positioned': False, 'raw': value}
            else:
                return {'pr_number': 0, 'executing': False, 'completed': False, 'positioned': False, 'raw': value}

        except Exception as e:
            logger.error(f"读取PR状态失败: {e}")
            self.increment_error()
            return {'pr_number': 0, 'executing': False, 'completed': False, 'positioned': False}

    def get_pr_status(self) -> Dict[str, Any]:
        """获取PR执行状态

        ASDB3通过两种方式获取PR状态：
        1. P5-007: 读取PR执行状态（推荐）
        2. P4-009: DO物理输出状态（bit0-bit5对应DO1-DO6）

        P4-009的bit位对应P2.018-P2.023分配的DO功能：
        - bit0: DO1输出状态
        - bit1: DO2输出状态
        - bit2: DO3输出状态
        - bit3: DO4输出状态
        - bit4: DO5输出状态
        - bit5: DO6输出状态

        需要结合P2.018-P2.023的DO功能分配来解析具体含义。

        Returns:
            包含pr执行状态和DO输出状态
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        try:
            result = {}

            pr_status = self.read_pr_status()
            result.update(pr_status)

            addr_p4_009 = self.calc_addr(4, 9)
            do_status = self.modbus.read_register(address=addr_p4_009, slave_id=self.slave_id)
            if do_status is not None:
                result['do_raw'] = do_status
                result['do1'] = bool(do_status & 0x01)
                result['do2'] = bool(do_status & 0x02)
                result['do3'] = bool(do_status & 0x04)
                result['do4'] = bool(do_status & 0x08)
                result['do5'] = bool(do_status & 0x10)
                result['do6'] = bool(do_status & 0x20)

            if self.platform_device:
                self.platform_device.record_operation(success=True)

            return result

        except Exception as e:
            logger.error(f"获取PR状态失败: {e}")
            self.increment_error()

            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return {}

    def get_pr_monitor_vars(self) -> Dict[str, Any]:
        """获取PR监控变量

        ASDB3监控变量读取方式（与ASDB2不同）：
        1. 写监控代码到P0.017-P0.021（选择监控寄存器1-5的内容）
        2. 读P0.009-P0.013（32位，获取监控寄存器1-5的值）

        监控代码（Table 8.3）：
        - 0x000: 反馈位置(Fb_PUU)
        - 0x001: 位置命令(Cmd_O)
        - 0x002: 跟随误差(Err_PUU)
        - 0x064: PR命令终点(Cmd_E)

        Returns:
            包含cmd_o, cmd_e, fb_puu, err_puu
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        try:
            monitor_codes = {
                'fb_puu': 0x000,
                'cmd_o': 0x001,
                'err_puu': 0x002,
                'cmd_e': 0x064,
            }

            monitor_select_addrs = [
                self.calc_addr(0, 17),
                self.calc_addr(0, 18),
                self.calc_addr(0, 19),
                self.calc_addr(0, 20),
            ]
            monitor_read_addrs = [
                self.calc_addr(0, 9),
                self.calc_addr(0, 10),
                self.calc_addr(0, 11),
                self.calc_addr(0, 12),
            ]

            items = list(monitor_codes.items())
            for i, (name, code) in enumerate(items):
                self.modbus.write_register(
                    address=monitor_select_addrs[i],
                    value=code,
                    slave_id=self.slave_id
                )
                time.sleep(0.03)

            time.sleep(0.05)

            monitor_vars = {}
            for i, (name, code) in enumerate(items):
                regs = self.modbus.read_registers(
                    address=monitor_read_addrs[i],
                    count=2,
                    slave_id=self.slave_id
                )
                monitor_vars[name] = self._read_32bit_signed(regs) if regs else 0

            if self.platform_device:
                self.platform_device.record_operation(success=True)

            return monitor_vars

        except Exception as e:
            logger.error(f"获取PR监控变量失败: {e}")
            self.increment_error()

            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return {}

    def _read_32bit_signed(self, regs):
        """读取32位有符号整数

        Args:
            regs: 寄存器列表（2个16位）

        Returns:
            32位有符号整数
        """
        if not regs or len(regs) < 2:
            return 0

        low_word = regs[0]
        high_word = regs[1]
        value = (high_word << 16) | low_word

        # 处理32位有符号整数
        if value & 0x80000000:
            value = value - 0x100000000

        return value

    def reset_error(self) -> bool:
        """复位错误

        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("电机驱动器未连接")

        try:
            # 复位错误（地址0x0214，bit 6）
            current_value = self.modbus.read_register(address=0x0214, slave_id=self.slave_id)
            if current_value is not None:
                # 设置bit 6
                reset_value = current_value | 0x0040
                self.modbus.write_register(address=0x0214, value=reset_value, slave_id=self.slave_id)
                time.sleep(0.1)

                # 清除bit 6
                clear_value = current_value & ~0x0040
                self.modbus.write_register(address=0x0214, value=clear_value, slave_id=self.slave_id)
                time.sleep(0.1)

            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)

            logger.info("错误已复位")
            return True

        except Exception as e:
            logger.error(f"复位错误失败: {e}")
            self.increment_error()

            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=False)

            return False