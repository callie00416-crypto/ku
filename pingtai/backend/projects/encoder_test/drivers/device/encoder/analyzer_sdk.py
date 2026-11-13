import sys
import os
import re
import serial.tools.list_ports

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/analyzerHost1.3')

from Analyzer import Analyzer
from Encoder import Encoder
from Defines import EncoderInterfaceRS485, EncoderReturnDirect
from DataFormatter import EncoderReadoutConfig, EncoderReadout
from CRC import calcCRC8

from shared.drivers.base.sdk_driver import SDKDriver
from typing import Dict, Any, Optional, List
import logging
import time

logger = logging.getLogger(__name__)


class AnalyzerSDK(SDKDriver):
    """KingKong Analyzer SDK 封装"""
    
    def __init__(self, driver_id: str = 'analyzer_sdk', com_port: str = None, **kwargs):
        super().__init__(driver_id, **kwargs)
        self.com_port = com_port
        self.analyzer = None
        self.encoder = None
    
    def initialize(self) -> bool:
        try:
            if not self.com_port:
                devices = Analyzer.list()
                if not devices:
                    logger.error("未找到 KingKong Analyzer 设备")
                    return False
                self.com_port = devices[0]
                logger.info(f"自动发现设备: {self.com_port}")
            
            self.analyzer = Analyzer(self.com_port)
            self.encoder = Encoder(self.analyzer)
            self.encoder.powerOn()
            self._is_initialized = True
            logger.info(f"Analyzer SDK 初始化成功，端口: {self.com_port}")
            return True
        except Exception as e:
            logger.error(f"Analyzer SDK 初始化失败: {e}", exc_info=True)
            return False
    
    def cleanup(self):
        if self.encoder:
            try:
                self.encoder.stop()
                self.encoder.powerOff()
            except Exception as e:
                logger.warning(f"清理编码器失败: {e}")
        self._is_initialized = False
        logger.info("Analyzer SDK 已清理")
    
    def execute_command(self, cmd: str, params: Dict[str, Any]) -> Optional[Any]:
        if not self._is_initialized:
            logger.error("SDK 未初始化")
            return None
        
        try:
            if cmd == 'read_angle':
                return self._read_angle(params.get('command', 0x64), 
                                    params.get('timeout', 1000))
            elif cmd == 'read_dual_angle':
                return self._read_dual_angle(params.get('timeout', 1000))
            elif cmd == 'set_zero':
                return self._set_zero()
            elif cmd == 'power_on':
                return self.encoder.powerOn()
            elif cmd == 'power_off':
                return self.encoder.powerOff()
            elif cmd == 'stop':
                return self.encoder.stop()
            else:
                logger.error(f"未知命令: {cmd}")
                return None
        except Exception as e:
            logger.error(f"执行命令失败 {cmd}: {e}", exc_info=True)
            self.increment_error()
            return None
    
    def _read_dual_angle(self, timeout: int = 1000) -> Optional[Dict[str, Any]]:
        """读取双编码器数据（DPT型号专用）"""
        try:
            config = EncoderReadoutConfig()
            config.interface = EncoderInterfaceRS485
            config.returnType = EncoderReturnDirect
            config.baudRate = 2500000
            config.followedData.length = 0
            config.request.uart.command = 0x33  # DPT双编码器命令
            config.request.uart.timeoutByteNum = 40

            readout = EncoderReadout()
            readout.configIndex = 0
            readout.times = 1
            readout.delayTime = 10

            self.encoder.setReadoutConfigs([config])
            self.encoder.setReadouts([readout])

            data = self.encoder.startAndReceive(1, 500, timeout=timeout)
            return self._parse_dual_response(data)
        except Exception as e:
            logger.error(f"读取双编码器数据失败: {e}", exc_info=True)
            return None
    
    def _parse_dual_response(self, data) -> Optional[Dict[str, Any]]:
        """解析双编码器响应数据（DPT格式）"""
        if not data:
            logger.warning("无数据可解析")
            return None

        results = []
        for i, package in enumerate(data):
            if isinstance(package, list):
                package = bytes(package)

            result = {
                'packet_index': i,
                'raw_data': list(package),
                'raw_hex': package.hex(' ')
            }

            logger.info(f"双编码器原始数据[{i}]: 长度={len(package)}, 内容={package.hex(' ')}")
            
            # DPT双编码器格式: A0 A1 A2 B0 B1 B2 CRC (7字节)
            if len(package) >= 7:
                # 解析内圈角度 (A0 A1 A2, LSB优先)
                inner_raw = (package[2] << 16) | (package[1] << 8) | package[0]
                inner_deg = inner_raw * 360.0 / (1 << 24)
                
                # 解析外圈角度 (B0 B1 B2, LSB优先)
                outer_raw = (package[5] << 16) | (package[4] << 8) | package[3]
                outer_deg = outer_raw * 360.0 / (1 << 24)
                
                # CRC校验
                crc_valid = (calcCRC8(package[:6], 0, 6) == package[6])
                
                result['encoder1'] = {
                    'angle_raw': inner_raw,
                    'angle_deg': inner_deg,
                    'crc_valid': crc_valid
                }
                result['encoder2'] = {
                    'angle_raw': outer_raw,
                    'angle_deg': outer_deg,
                    'crc_valid': crc_valid
                }
                result['dual_mode'] = True
            else:
                logger.warning(f"数据包长度不足: {len(package)}字节")
                continue

            results.append(result)

        if results:
            return results[0]
        return None
    
    def _parse_single_encoder(self, package: bytes) -> Dict[str, Any]:
        """解析单个编码器的数据"""
        result = {}
        
        if len(package) >= 7:
            circles = (package[1] << 8) | package[0]
            angle_raw = (package[4] << 16) | (package[3] << 8) | package[2]
            angle = angle_raw * 360 / (1 << 24)
            
            crc_data = package[:6]
            received_crc = package[6]
            calculated_crc = calcCRC8(crc_data, 0, len(crc_data))
            
            result.update({
                'circles': circles,
                'angle_raw': angle_raw,
                'angle_degrees': round(angle, 4),
                'status': package[5],
                'crc': received_crc,
                'crc_valid': (received_crc == calculated_crc),
                'raw_hex': package.hex(' ')
            })
            
            logger.info(f"单编码器解析: 圈数={circles}, 角度={angle:.4f}°, CRC={received_crc == calculated_crc}")
        
        return result
    
    def _read_angle(self, command: int = 0x64, timeout: int = 1000) -> Optional[Dict[str, Any]]:
        try:
            config = EncoderReadoutConfig()
            config.interface = EncoderInterfaceRS485
            config.returnType = EncoderReturnDirect
            config.baudRate = 2500000
            config.followedData.length = 0
            config.request.uart.command = command
            config.request.uart.timeoutByteNum = 10

            readout = EncoderReadout()
            readout.configIndex = 0
            readout.times = 1
            readout.delayTime = 10

            self.encoder.setReadoutConfigs([config])
            self.encoder.setReadouts([readout])

            data = self.encoder.startAndReceive(1, 500, timeout=timeout)
            return self._parse_response(data)
        except Exception as e:
            logger.error(f"读取角度失败: {e}", exc_info=True)
            return None
    
    def _set_zero(self) -> bool:
        try:
            result = self.encoder.setZero()
            return result is not None
        except Exception as e:
            logger.error(f"设置零点失败: {e}", exc_info=True)
            return False
    
    def _parse_response(self, data) -> Optional[Dict[str, Any]]:
        if not data:
            logger.warning("无数据可解析")
            return None

        results = []
        try:
            resolved_data = Encoder.resolvePackages(data)
            logger.info(f"解析到 {len(resolved_data)} 个数据包")
            
            for i, (trigger, trigger_data) in enumerate(resolved_data):
                if trigger_data is None:
                    continue
                    
                result = {
                    'packet_index': i,
                    'raw_data': list(trigger_data),
                    'raw_hex': trigger_data.hex(' ')
                }
                
                logger.info(f"解析数据[{i}]: 长度={len(trigger_data)}, 内容={trigger_data.hex(' ')}")
                
                if len(trigger_data) >= 7:
                    circles = (trigger_data[1] << 8) | trigger_data[0]
                    angle_raw = (trigger_data[2] << 16) | (trigger_data[3] << 8) | trigger_data[4]
                    angle = angle_raw * 360 / (1 << 24)
                    status = trigger_data[5]
                    crc_data = trigger_data[:6]
                    received_crc = trigger_data[6]
                    calculated_crc = calcCRC8(crc_data, 0, len(crc_data))
                    
                    result.update({
                        'circles': circles,
                        'angle_raw': angle_raw,
                        'angle_degrees': round(angle, 4),
                        'status': status,
                        'crc': received_crc,
                        'crc_valid': (received_crc == calculated_crc)
                    })
                    logger.info(f"7字节模式(24BM): 圈数={circles}, 角度={angle:.4f}°, CRC={received_crc == calculated_crc}")
                    
                elif len(trigger_data) >= 5:
                    angle_raw = (trigger_data[0] << 16) | (trigger_data[1] << 8) | trigger_data[2]
                    angle = angle_raw * 360 / (1 << 24)
                    status = trigger_data[3]
                    
                    result.update({
                        'angle_raw': angle_raw,
                        'angle_degrees': round(angle, 4),
                        'status': status,
                        'circles': 0
                    })
                    logger.info(f"5字节模式: 角度={angle:.4f}°, 状态=0x{status:02X}")
                    
                elif len(trigger_data) >= 3:
                    angle_raw = (trigger_data[0] << 16) | (trigger_data[1] << 8) | trigger_data[2]
                    angle = angle_raw * 360 / (1 << 24)
                    
                    result.update({
                        'angle_raw': angle_raw,
                        'angle_degrees': round(angle, 4),
                        'circles': 0,
                        'status': 0,
                        'crc_valid': True
                    })
                    logger.info(f"3字节模式: 角度={angle:.4f}°")
                
                results.append(result)
                
        except Exception as e:
            logger.error(f"解析数据失败: {e}", exc_info=True)
            return None

        if results:
            return results[0]
        return None
    
    @staticmethod
    def list_devices() -> List[str]:
        """列出可用的 Analyzer 设备"""
        VCOM = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            port_str = str(port)
            match = re.search(r'KingKong Analyzer \((.*?)\)', port_str)
            if match:
                VCOM.append(match.group(1))
        return VCOM