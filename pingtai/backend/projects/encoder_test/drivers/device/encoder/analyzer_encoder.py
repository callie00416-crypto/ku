from shared.drivers.base.base_device import BaseDevice
from .analyzer_sdk import AnalyzerSDK
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AnalyzerEncoderDriver(BaseDevice):
    """基于 KingKong Analyzer 的编码器驱动"""
    
    BAUD_RATE = 2500000
    COMMAND_READ_ANGLE = 0x64
    COMMAND_ZERO = 0x1A
    
    def __init__(self, driver_id: str = 'analyzer_encoder', 
                 com_port: str = None, protocol=None, **kwargs):
        super().__init__(driver_id, protocol=protocol, **kwargs)
        self.sdk = AnalyzerSDK(driver_id=f"{driver_id}_sdk", com_port=com_port)
        self._angle = 0.0
        self._circles = 0
        self._status = 0
        self._crc_valid = True
    
    def connect(self) -> bool:
        try:
            if self.sdk.initialize():
                self._is_connected = True
                self._device_status = "connected"
                logger.info(f"编码器驱动连接成功: {self.driver_id}")
                return True
            else:
                self._device_status = "connection_failed"
                return False
        except Exception as e:
            logger.error(f"编码器连接失败: {e}", exc_info=True)
            self._device_status = "error"
            return False
    
    def disconnect(self):
        try:
            self.sdk.cleanup()
        finally:
            self._is_connected = False
            self._device_status = "disconnected"
            logger.info(f"编码器驱动已断开: {self.driver_id}")
    
    def read_data(self) -> Dict[str, Any]:
        """读取单编码器数据"""
        if not self._is_connected:
            raise ConnectionError("编码器未连接")
        
        try:
            result = self.sdk.execute_command('read_angle', {
                'command': self.COMMAND_READ_ANGLE,
                'timeout': 1000
            })
            
            if result:
                self._angle = result.get('angle_degrees', 0.0)
                self._circles = result.get('circles', 0)
                self._status = result.get('status', 0)
                self._crc_valid = result.get('crc_valid', True)
                
                logger.debug(f"读取编码器数据 - 角度: {self._angle}°, 圈数: {self._circles}, CRC: {self._crc_valid}")
            
            return {
                'angle': self._angle,
                'angle_degrees': self._angle,
                'circles': self._circles,
                'status': self._status,
                'crc_valid': self._crc_valid,
                'raw_data': result.get('raw_data', []) if result else [],
                'raw_hex': result.get('raw_hex', '') if result else ''
            }
        except Exception as e:
            logger.error(f"读取编码器数据失败: {e}", exc_info=True)
            self.increment_error()
            return {
                'angle': self._angle,
                'circles': self._circles,
                'status': self._status,
                'crc_valid': False,
                'raw_data': [],
                'raw_hex': '',
                'error': str(e)
            }
    
    def read_dual_data(self) -> Dict[str, Any]:
        """读取双编码器数据（DPT型号专用）"""
        if not self._is_connected:
            raise ConnectionError("编码器未连接")

        encoder1 = None
        encoder2 = None

        try:
            result = self.sdk.execute_command('read_dual_angle', {
                'timeout': 1000
            })

            if result:
                encoder1 = result.get('encoder1', {})
                encoder2 = result.get('encoder2', {})

                angle1 = encoder1.get('angle_degrees', 0.0)
                angle2 = encoder2.get('angle_degrees', 0.0) if encoder2 else None

                logger.debug(f"读取双编码器数据 - 编码器1: {angle1}°, 编码器2: {angle2}°")

            return {
                'dual_mode': result.get('dual_mode', False) if result else False,
                'encoder1': {
                    'angle': encoder1.get('angle_deg', 0.0),
                    'angle_degrees': encoder1.get('angle_deg', 0.0),
                    'angle_raw': encoder1.get('angle_raw', 0),
                    'circles': encoder1.get('circles', 0),
                    'status': encoder1.get('status', 0),
                    'crc_valid': encoder1.get('crc_valid', False),
                    'raw_hex': encoder1.get('raw_hex', '')
                } if encoder1 else None,
                'encoder2': {
                    'angle': encoder2.get('angle_deg', 0.0),
                    'angle_degrees': encoder2.get('angle_deg', 0.0),
                    'angle_raw': encoder2.get('angle_raw', 0),
                    'circles': encoder2.get('circles', 0),
                    'status': encoder2.get('status', 0),
                    'crc_valid': encoder2.get('crc_valid', False),
                    'raw_hex': encoder2.get('raw_hex', '')
                } if encoder2 else None,
                'raw_data': result.get('raw_data', []) if result else [],
                'raw_hex': result.get('raw_hex', '') if result else ''
            }
        except Exception as e:
            logger.error(f"读取双编码器数据失败: {e}", exc_info=True)
            self.increment_error()
            return {
                'dual_mode': False,
                'encoder1': None,
                'encoder2': None,
                'error': str(e)
            }

    def read_both_angles(self) -> Dict[str, Any]:
        """读取双圈角度（内圈+外圈）
        
        返回格式与 TestCase 层期望一致：
        {'inner': {'angle_deg': ..., 'angle_raw': ...},
         'outer': {'angle_deg': ..., 'angle_raw': ...},
         'crc_valid': bool}
        """
        if not self._is_connected:
            raise ConnectionError("编码器未连接")

        try:
            dual_data = self.read_dual_data()
            encoder1 = dual_data.get('encoder1')
            encoder2 = dual_data.get('encoder2')
            print(f"[DEBUG read_both_angles] dual_data keys={list(dual_data.keys())}, encoder1={bool(encoder1)}, encoder2={bool(encoder2)}")

            if encoder1:
                inner = {
                    'angle_deg': encoder1.get('angle_degrees', 0.0),
                    'angle_raw': encoder1.get('angle_raw', 0)
                }
                outer = {
                    'angle_deg': encoder2.get('angle_degrees', 0.0) if encoder2 else 0.0,
                    'angle_raw': encoder2.get('angle_raw', 0) if encoder2 else 0
                }
                crc_valid = encoder1.get('crc_valid', False) and (
                    encoder2.get('crc_valid', True) if encoder2 else True
                )
            else:
                single = self.read_data()
                print(f"[DEBUG read_both_angles] fallback to single: {single}")
                inner = {
                    'angle_deg': single.get('angle_degrees', 0.0),
                    'angle_raw': 0
                }
                outer = dict(inner)
                crc_valid = single.get('crc_valid', False)

            result = {
                'inner': inner,
                'outer': outer,
                'crc_valid': crc_valid
            }
            print(f"[DEBUG read_both_angles] result keys={list(result.keys())}, crc_valid={crc_valid}, inner_angle={inner['angle_deg']}")
            return result
        except Exception as e:
            logger.error(f"读取双圈角度失败: {e}", exc_info=True)
            self.increment_error()
            return {
                'inner': {'angle_deg': 0.0, 'angle_raw': 0},
                'outer': {'angle_deg': 0.0, 'angle_raw': 0},
                'crc_valid': False,
                'error': str(e)
            }

    def write_data(self, data: Dict[str, Any]) -> bool:
        try:
            if 'zero' in data and data['zero']:
                return self.set_zero()
            elif 'command' in data:
                result = self.sdk.execute_command('read_angle', {
                    'command': data['command'],
                    'timeout': data.get('timeout', 1000)
                })
                return result is not None
            return True
        except Exception as e:
            logger.error(f"写入编码器数据失败: {e}", exc_info=True)
            self.increment_error()
            return False
    
    def reset(self):
        """重置编码器（设置零点）"""
        self.set_zero()
    
    def set_zero(self) -> bool:
        """设置编码器零点"""
        if not self._is_connected:
            raise ConnectionError("编码器未连接")
        
        try:
            result = self.sdk.execute_command('set_zero', {})
            if result:
                self._angle = 0.0
                self._circles = 0
                logger.info(f"编码器已设置零点: {self.driver_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"设置零点失败: {e}", exc_info=True)
            self.increment_error()
            return False
    
    def power_on(self) -> bool:
        """编码器上电"""
        try:
            result = self.sdk.execute_command('power_on', {})
            return result is not None
        except Exception as e:
            logger.error(f"编码器上电失败: {e}", exc_info=True)
            return False
    
    def power_off(self) -> bool:
        """编码器断电"""
        try:
            result = self.sdk.execute_command('power_off', {})
            return result is not None
        except Exception as e:
            logger.error(f"编码器断电失败: {e}", exc_info=True)
            return False
    
    def stop(self):
        """停止编码器采集"""
        self.sdk.execute_command('stop', {})
    
    def health_check(self) -> Dict[str, Any]:
        base = super().health_check()
        base.update({
            'angle': self._angle,
            'circles': self._circles,
            'status': self._status,
            'crc_valid': self._crc_valid,
            'sdk_status': self.sdk.health_check()
        })
        return base
    
    @classmethod
    def list_devices(cls) -> list:
        """列出可用的编码器设备"""
        return AnalyzerSDK.list_devices()