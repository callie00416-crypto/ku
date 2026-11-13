import sys
import os
import time
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/analyzerHost1.3')

from Analyzer import Analyzer
from Encoder import Encoder
from Defines import EncoderInterfaceRS485, EncoderReturnDirect
from DataFormatter import EncoderReadoutConfig, EncoderReadout
from CRC import calcCRC8

import logging

logger = logging.getLogger(__name__)

class DPTEncoderAnalyzer:
    """
    DPT磁双编码器通过Analyzer硬件的驱动
    
    协议特点（根据DPT数据手册）：
    - 接口：RS485
    - 波特率：2.5 Mbps 或 5 Mbps
    - 字节顺序：LSB优先
    - 命令：
      - 0x31: 获取内圈角度 (4字节: A0 A1 A2 CRC)
      - 0x32: 获取外圈角度 (4字节: B0 B1 B2 CRC)
      - 0x33: 获取双角度 (7字节: A0 A1 A2 B0 B1 B2 CRC)
      - 0x43: 获取双角度+状态 (8字节)
    """
    
    CMD_GET_INNER_ANGLE = 0x31
    CMD_GET_OUTER_ANGLE = 0x32
    CMD_GET_BOTH_ANGLE = 0x33
    CMD_GET_BOTH_WITH_STATUS = 0x43
    
    def __init__(self, port='COM5', baud_rate=2500000):
        self.port = port
        self.baud_rate = baud_rate
        self.analyzer = None
        self.encoder = None
        self._connected = False
        
    def connect(self):
        """建立连接"""
        try:
            self.analyzer = Analyzer(self.port)
            self.encoder = Encoder(self.analyzer)
            self.encoder.powerOn()
            self._connected = True
            logger.info(f"DPT编码器通过Analyzer连接成功: {self.port}")
            return True
        except Exception as e:
            logger.error(f"DPT编码器连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self._connected:
            try:
                self.encoder.stop()
                self.encoder.powerOff()
                self._connected = False
                logger.info("DPT编码器已断开")
            except Exception as e:
                logger.error(f"断开连接失败: {e}")
    
    def is_connected(self):
        """检查连接状态"""
        return self._connected
    
    def _configure(self, command, timeout_byte_num=20):
        """配置编码器读取参数"""
        config = EncoderReadoutConfig()
        config.interface = EncoderInterfaceRS485
        config.returnType = EncoderReturnDirect
        config.baudRate = self.baud_rate
        config.followedData.length = 0
        config.request.uart.command = command
        config.request.uart.timeoutByteNum = timeout_byte_num
        
        readout = EncoderReadout()
        readout.configIndex = 0
        readout.times = 1
        readout.delayTime = 10
        
        self.encoder.setReadoutConfigs([config])
        self.encoder.setReadouts([readout])
    
    def _read_data(self, command, expected_length, timeout=1000):
        """读取数据"""
        if not self._connected:
            raise ConnectionError("编码器未连接")
        
        try:
            self._configure(command)
            data = self.encoder.startAndReceive(1, 500, timeout=timeout)
            
            if data and len(data) > 0:
                return bytes(data[0])
            return None
            
        except Exception as e:
            logger.error(f"读取数据失败: {e}")
            return None
    
    def _parse_angle(self, data):
        """解析24位角度数据（LSB优先）"""
        if len(data) >= 3:
            angle_raw = (data[2] << 16) | (data[1] << 8) | data[0]
            angle_deg = angle_raw * 360.0 / (1 << 24)
            return angle_raw, angle_deg
        return None, None
    
    def read_inner_angle(self):
        """读取内圈角度"""
        data = self._read_data(self.CMD_GET_INNER_ANGLE, 4)
        if data and len(data) >= 4:
            angle_raw, angle_deg = self._parse_angle(data[:3])
            crc_valid = (calcCRC8(data[:3], 0, 3) == data[3])
            return {
                'angle_raw': angle_raw,
                'angle_deg': angle_deg,
                'crc_valid': crc_valid,
                'raw_data': list(data)
            }
        return None
    
    def read_outer_angle(self):
        """读取外圈角度"""
        data = self._read_data(self.CMD_GET_OUTER_ANGLE, 4)
        if data and len(data) >= 4:
            angle_raw, angle_deg = self._parse_angle(data[:3])
            crc_valid = (calcCRC8(data[:3], 0, 3) == data[3])
            return {
                'angle_raw': angle_raw,
                'angle_deg': angle_deg,
                'crc_valid': crc_valid,
                'raw_data': list(data)
            }
        return None
    
    def read_both_angles(self):
        """读取内圈和外圈角度"""
        data = self._read_data(self.CMD_GET_BOTH_ANGLE, 7)
        if data and len(data) >= 7:
            inner_raw, inner_deg = self._parse_angle(data[0:3])
            outer_raw, outer_deg = self._parse_angle(data[3:6])
            crc_valid = (calcCRC8(data[:6], 0, 6) == data[6])
            return {
                'inner': {
                    'angle_raw': inner_raw,
                    'angle_deg': inner_deg
                },
                'outer': {
                    'angle_raw': outer_raw,
                    'angle_deg': outer_deg
                },
                'crc_valid': crc_valid,
                'raw_data': list(data)
            }
        return None
    
    def read_both_with_status(self):
        """读取内圈和外圈角度及状态"""
        data = self._read_data(self.CMD_GET_BOTH_WITH_STATUS, 8)
        if data and len(data) >= 8:
            inner_raw, inner_deg = self._parse_angle(data[0:3])
            outer_raw, outer_deg = self._parse_angle(data[3:6])
            status = data[6]
            crc_valid = (calcCRC8(data[:7], 0, 7) == data[7])
            
            status_info = {
                'error': (status & 0x80) != 0,
                'outer_angle_error': (status & 0x10) != 0,
                'inner_angle_error': (status & 0x08) != 0
            }
            
            return {
                'inner': {
                    'angle_raw': inner_raw,
                    'angle_deg': inner_deg
                },
                'outer': {
                    'angle_raw': outer_raw,
                    'angle_deg': outer_deg
                },
                'status': status,
                'status_info': status_info,
                'crc_valid': crc_valid,
                'raw_data': list(data)
            }
        return None
    
    def reset(self):
        """重置设备"""
        logger.info(f"重置Analyzer编码器: {self.port}")
        self.disconnect()
        self.connect()
    
    def write_data(self, data: Any) -> bool:
        """写入数据（编码器通常只读，此方法保留接口兼容性）"""
        logger.warning("Analyzer编码器为只读设备，不支持写入数据")
        return False
    
    def __del__(self):
        """析构函数 - 不再自动断开连接，由用户手动控制"""
        pass

# 测试函数
def test_dpt_analyzer(port='COM6', baud_rate=2500000, read_count=10):
    logging.basicConfig(level=logging.INFO)
    
    encoder = DPTEncoderAnalyzer(port=port, baud_rate=baud_rate)
    
    try:
        if encoder.connect():
            print("\n=== DPT双编码器测试 (通过Analyzer) ===")
            print(f"端口: {port}, 波特率: {baud_rate}")
            print(f"连续读取角度 {read_count} 次\n")
            
            # 连续读取角度
            for i in range(read_count):
                result = encoder.read_both_angles()
                if result and result['crc_valid']:
                    inner_deg = result['inner']['angle_deg']
                    outer_deg = result['outer']['angle_deg']
                    print(f"[{i+1:2d}] 内圈: {inner_deg:8.4f}° | 外圈: {outer_deg:8.4f}° | CRC: ✅")
                elif result:
                    print(f"[{i+1:2d}] 内圈: {'N/A':>8} | 外圈: {'N/A':>8} | CRC: ❌")
                else:
                    print(f"[{i+1:2d}] 读取失败")
                
                time.sleep(0.05)
            
            print("\n=== 测试完成 ===")
            
        else:
            print("编码器连接失败")
            
    finally:
        encoder.disconnect()

if __name__ == "__main__":
    test_dpt_analyzer()