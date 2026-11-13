"""
设备串口配置管理器 - Device Serial Port Configuration Manager

【职责】
管理设备的串口配置
自动检测设备串口
提供设备串口映射
支持设备识别和验证

【解决的问题】
1. 多设备串口管理混乱
2. 串口号经常变化
3. 设备识别困难
4. 配置维护复杂

【工业应用】
工业自动化测试平台中，需要管理大量硬件设备
每个设备都有固定的串口配置
需要统一的配置管理和自动检测
"""
import os
import json
import logging
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from shared.drivers.comm.serial_port_manager import get_serial_port_manager, SerialPortStatus

logger = logging.getLogger(__name__)


@dataclass
class DeviceSerialConfig:
    """设备串口配置"""
    device_id: str              # 设备ID
    device_name: str            # 设备名称
    device_type: str            # 设备类型
    port: str                   # 串口号
    baudrate: int               # 波特率
    data_bits: int              # 数据位
    stop_bits: int              # 停止位
    parity: str                 # 校验位
    flow_control: str           # 流控制
    timeout: int                # 超时时间
    auto_detect: bool = False   # 是否自动检测
    verify_command: Optional[str] = None  # 验证命令
    verify_response: Optional[str] = None # 验证响应
    description: str = ""       # 描述
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceSerialConfig':
        """从字典创建"""
        return cls(**data)


class DeviceSerialConfigManager:
    """设备串口配置管理器（单例模式）"""
    
    _instance: Optional['DeviceSerialConfigManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._configs: Dict[str, DeviceSerialConfig] = {}
        self._config_file: Optional[Path] = None
        self._port_manager = get_serial_port_manager()
        
        logger.info("设备串口配置管理器初始化完成")
    
    def load_config_file(self, config_file: str):
        """加载配置文件
        
        Args:
            config_file: 配置文件路径
        """
        self._config_file = Path(config_file)
        
        if not self._config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}")
            self._configs = {}
            return
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._configs = {}
            for device_id, config_data in data.items():
                self._configs[device_id] = DeviceSerialConfig.from_dict(config_data)
            
            logger.info(f"已加载 {len(self._configs)} 个设备配置")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._configs = {}
    
    def save_config_file(self):
        """保存配置文件"""
        if not self._config_file:
            logger.warning("未设置配置文件路径")
            return
        
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            for device_id, config in self._configs.items():
                data[device_id] = config.to_dict()
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置文件已保存: {self._config_file}")
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def add_device_config(self, config: DeviceSerialConfig):
        """添加设备配置
        
        Args:
            config: 设备配置
        """
        self._configs[config.device_id] = config
        logger.info(f"已添加设备配置: {config.device_id} ({config.device_name})")
    
    def get_device_config(self, device_id: str) -> Optional[DeviceSerialConfig]:
        """获取设备配置
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备配置或None
        """
        return self._configs.get(device_id)
    
    def remove_device_config(self, device_id: str):
        """移除设备配置
        
        Args:
            device_id: 设备ID
        """
        if device_id in self._configs:
            del self._configs[device_id]
            logger.info(f"已移除设备配置: {device_id}")
    
    def list_device_configs(self) -> List[DeviceSerialConfig]:
        """列出所有设备配置"""
        return list(self._configs.values())
    
    def get_device_port(self, device_id: str) -> Optional[str]:
        """获取设备串口号
        
        Args:
            device_id: 设备ID
            
        Returns:
            串口号或None
        """
        config = self.get_device_config(device_id)
        return config.port if config else None
    
    def auto_detect_device_port(self, device_id: str) -> Optional[str]:
        """自动检测设备串口
        
        Args:
            device_id: 设备ID
            
        Returns:
            检测到的串口号或None
        """
        config = self.get_device_config(device_id)
        if not config:
            logger.warning(f"未找到设备配置: {device_id}")
            return None
        
        if not config.auto_detect:
            logger.info(f"设备 {device_id} 未启用自动检测")
            return config.port
        
        logger.info(f"开始自动检测设备 {device_id} 的串口...")
        
        # 获取所有可用串口
        available_ports = self._port_manager.list_available_ports()
        
        if not available_ports:
            logger.warning("未找到可用串口")
            return None
        
        logger.info(f"找到 {len(available_ports)} 个可用串口")
        
        # 尝试每个串口
        for port in available_ports:
            logger.info(f"尝试串口: {port}")
            
            # 检查串口状态
            status = self._port_manager.check_port_status(port)
            if status != SerialPortStatus.FREE:
                logger.info(f"串口 {port} 状态: {status.value}，跳过")
                continue
            
            # 尝试连接设备
            try:
                import serial
                ser = serial.Serial(
                    port=port,
                    baudrate=config.baudrate,
                    bytesize=config.data_bits,
                    stopbits=config.stop_bits,
                    parity=config.parity,
                    timeout=config.timeout / 1000.0
                )
                
                # 如果有验证命令，发送验证命令
                if config.verify_command:
                    ser.write(config.verify_command.encode('ascii'))
                    response = ser.read_all().decode('ascii', errors='ignore').strip()
                    
                    if config.verify_response and config.verify_response in response:
                        logger.info(f"✓ 串口 {port} 验证成功")
                        ser.close()
                        return port
                    else:
                        logger.info(f"✗ 串口 {port} 验证失败")
                        ser.close()
                        continue
                else:
                    # 没有验证命令，直接返回第一个可用串口
                    logger.info(f"✓ 串口 {port} 可用（无验证）")
                    ser.close()
                    return port
                    
            except Exception as e:
                logger.warning(f"串口 {port} 连接失败: {e}")
                continue
        
        logger.warning(f"未找到设备 {device_id} 的串口")
        return None
    
    def update_device_port(self, device_id: str, new_port: str):
        """更新设备串口号
        
        Args:
            device_id: 设备ID
            new_port: 新串口号
        """
        config = self.get_device_config(device_id)
        if config:
            old_port = config.port
            config.port = new_port
            logger.info(f"设备 {device_id} 串口已更新: {old_port} -> {new_port}")
        else:
            logger.warning(f"未找到设备配置: {device_id}")
    
    def verify_device_connection(self, device_id: str) -> bool:
        """验证设备连接
        
        Args:
            device_id: 设备ID
            
        Returns:
            是否连接成功
        """
        config = self.get_device_config(device_id)
        if not config:
            logger.warning(f"未找到设备配置: {device_id}")
            return False
        
        try:
            import serial
            ser = serial.Serial(
                port=config.port,
                baudrate=config.baudrate,
                bytesize=config.data_bits,
                stopbits=config.stop_bits,
                parity=config.parity,
                timeout=config.timeout / 1000.0
            )
            
            # 如果有验证命令，发送验证命令
            if config.verify_command:
                ser.write(config.verify_command.encode('ascii'))
                response = ser.read_all().decode('ascii', errors='ignore').strip()
                
                if config.verify_response and config.verify_response in response:
                    logger.info(f"设备 {device_id} 连接验证成功")
                    ser.close()
                    return True
                else:
                    logger.warning(f"设备 {device_id} 连接验证失败")
                    ser.close()
                    return False
            else:
                logger.info(f"设备 {device_id} 连接成功（无验证）")
                ser.close()
                return True
                
        except Exception as e:
            logger.error(f"设备 {device_id} 连接失败: {e}")
            return False
    
    def get_all_devices_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有设备状态"""
        result = {}
        
        for device_id, config in self._configs.items():
            port_status = self._port_manager.check_port_status(config.port)
            connection_status = self.verify_device_connection(device_id)
            
            result[device_id] = {
                'device_name': config.device_name,
                'device_type': config.device_type,
                'port': config.port,
                'port_status': port_status.value,
                'connection_status': connection_status,
                'auto_detect': config.auto_detect
            }
        
        return result


# 全局单例
_device_config_manager = None


def get_device_config_manager() -> DeviceSerialConfigManager:
    """获取设备串口配置管理器单例"""
    global _device_config_manager
    if _device_config_manager is None:
        _device_config_manager = DeviceSerialConfigManager()
    return _device_config_manager


def load_device_config_file(config_file: str):
    """加载设备配置文件（便捷函数）"""
    manager = get_device_config_manager()
    manager.load_config_file(config_file)


def get_device_port(device_id: str, auto_detect: bool = False) -> Optional[str]:
    """获取设备串口号（便捷函数）
    
    Args:
        device_id: 设备ID
        auto_detect: 是否自动检测
        
    Returns:
        串口号或None
    """
    manager = get_device_config_manager()
    
    if auto_detect:
        return manager.auto_detect_device_port(device_id)
    else:
        return manager.get_device_port(device_id)


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("设备串口配置管理器测试")
    print("=" * 60)
    
    manager = get_device_config_manager()
    
    # 创建测试配置
    config = DeviceSerialConfig(
        device_id="power_amplifier",
        device_name="ATA-101B功率放大器",
        device_type="power_amplifier",
        port="COM1",
        baudrate=9600,
        data_bits=8,
        stop_bits=1,
        parity="none",
        flow_control="none",
        timeout=1000,
        auto_detect=True,
        description="用于编码器测试的功率放大器"
    )
    
    # 添加配置
    manager.add_device_config(config)
    
    # 获取设备串口
    port = manager.get_device_port("power_amplifier")
    print(f"\n设备串口: {port}")
    
    # 列出所有设备
    configs = manager.list_device_configs()
    print(f"\n设备列表:")
    for cfg in configs:
        print(f"  - {cfg.device_id}: {cfg.device_name} ({cfg.port})")
    
    # 获取设备状态
    status = manager.get_all_devices_status()
    print(f"\n设备状态:")
    for device_id, info in status.items():
        print(f"  - {device_id}:")
        print(f"    端口: {info['port']}")
        print(f"    端口状态: {info['port_status']}")
        print(f"    连接状态: {info['connection_status']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)