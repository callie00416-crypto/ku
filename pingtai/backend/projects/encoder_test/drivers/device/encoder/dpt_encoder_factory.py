import sys
import os

# 设置正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 先导入同目录下的模块
from dpt_encoder_rs485 import DPTEncoderRS485
from dpt_encoder_bissc import DPTEncoderBISSC
from dpt_encoder_analyzer import DPTEncoderAnalyzer

# 然后尝试导入基础设备类
try:
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
    sys.path.insert(0, backend_dir)
    from shared.drivers.base.base_device import BaseDevice
    HAS_BASE_DEVICE = True
except ImportError:
    # 如果没有BaseDevice，创建一个简单的基类
    class BaseDevice:
        def __init__(self, driver_id, **kwargs):
            self.driver_id = driver_id
            self._is_connected = False
            self._device_status = "disconnected"
    HAS_BASE_DEVICE = False

from typing import Dict, Any, Optional, Type
import logging

logger = logging.getLogger(__name__)


class DPTEncoderFactory:
    """
    DPT磁双编码器驱动工厂
    
    支持协议：
    - RS485: 通过串口直接通信
    - BISS-C: 通过SPI模拟BISS-C时序
    - ANALYZER: 通过KingKong Analyzer硬件转接
    """
    
    PROTOCOLS = {
        'RS485': DPTEncoderRS485,
        'BISS-C': DPTEncoderBISSC,
        'ANALYZER': DPTEncoderAnalyzer
    }
    
    @classmethod
    def create(cls, protocol: str, **kwargs) -> Optional[BaseDevice]:
        """创建编码器驱动实例"""
        protocol = protocol.upper()
        
        if protocol not in cls.PROTOCOLS:
            logger.error(f"不支持的协议类型: {protocol}")
            logger.error(f"支持的协议: {list(cls.PROTOCOLS.keys())}")
            return None
        
        driver_class = cls.PROTOCOLS[protocol]
        
        try:
            encoder = driver_class(**kwargs)
            logger.info(f"创建{protocol}编码器驱动成功")
            return encoder
        except Exception as e:
            logger.error(f"创建{protocol}编码器驱动失败: {e}", exc_info=True)
            return None
    
    @classmethod
    def get_supported_protocols(cls) -> list:
        """获取支持的协议列表"""
        return list(cls.PROTOCOLS.keys())


class DPTEncoder(BaseDevice):
    """
    DPT磁双编码器统一驱动接口
    
    支持多种协议，提供一致的API接口
    """
    
    def __init__(self, protocol: str = 'RS485', **kwargs):
        """初始化编码器"""
        driver_id = kwargs.get('driver_id', f'dpt_encoder_{protocol.lower()}')
        super().__init__(driver_id, **kwargs)
        
        self._protocol = protocol
        self._inner_driver = DPTEncoderFactory.create(protocol, **kwargs)
    
    def connect(self) -> bool:
        """建立连接"""
        if self._inner_driver:
            result = self._inner_driver.connect()
            if result:
                self._is_connected = True
                self._device_status = "connected"
            else:
                self._device_status = "connection_failed"
            return result
        return False
    
    def disconnect(self):
        """断开连接"""
        if self._inner_driver:
            self._inner_driver.disconnect()
        self._is_connected = False
        self._device_status = "disconnected"
    
    def read_data(self) -> Dict[str, Any]:
        """读取数据"""
        if not self._is_connected:
            logger.error("编码器未连接")
            return None
        
        if self._inner_driver:
            return self._inner_driver.read_data()
        return None
    
    def read_inner_angle(self) -> Optional[Dict[str, Any]]:
        """读取内圈角度"""
        if self._inner_driver:
            return self._inner_driver.read_inner_angle()
        return None
    
    def read_outer_angle(self) -> Optional[Dict[str, Any]]:
        """读取外圈角度"""
        if self._inner_driver:
            return self._inner_driver.read_outer_angle()
        return None
    
    def read_both_angles(self) -> Optional[Dict[str, Any]]:
        """读取双角度"""
        if self._inner_driver:
            return self._inner_driver.read_both_angles()
        return None
    
    def reset(self):
        """重置设备"""
        logger.info(f"重置编码器: {self.driver_id}")
        self.disconnect()
        self.connect()
    
    def write_data(self, data: Any) -> bool:
        """写入数据（编码器通常只读，此方法保留接口兼容性）"""
        logger.warning("编码器为只读设备，不支持写入数据")
        return False


# 测试函数
def test_dpt_encoder_factory():
    logging.basicConfig(level=logging.INFO)
    
    print("=== DPT编码器工厂测试 ===")
    
    for protocol in ['RS485', 'BISS-C', 'ANALYZER']:
        print(f"\n--- 测试{protocol}协议 ---")
        
        try:
            if protocol == 'RS485':
                encoder = DPTEncoder(protocol=protocol, port='COM5', baud_rate=2500000)
            elif protocol == 'BISS-C':
                encoder = DPTEncoder(protocol=protocol, spi_bus=0, spi_cs=0)
            elif protocol == 'ANALYZER':
                encoder = DPTEncoder(protocol=protocol, port='COM5', baud_rate=2500000)
            
            if encoder.connect():
                result = encoder.read_both_angles()
                if result:
                    print(f"读取成功:")
                    if 'inner' in result and 'outer' in result:
                        print(f"  内圈角度: {result['inner']['angle_deg']:.4f}°")
                        print(f"  外圈角度: {result['outer']['angle_deg']:.4f}°")
                        print(f"  CRC校验: {'通过' if result.get('crc_valid', False) else '失败'}")
                    else:
                        print(f"  数据: {result}")
                else:
                    print(f"读取失败")
                
                encoder.disconnect()
            else:
                print(f"连接失败{'（模拟模式继续）' if protocol == 'BISS-C' else ''}")
                
        except Exception as e:
            print(f"测试{protocol}失败: {e}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_dpt_encoder_factory()