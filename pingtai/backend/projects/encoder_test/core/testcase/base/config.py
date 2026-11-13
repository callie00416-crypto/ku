"""
测试配置管理

支持 YAML 配置加载和 dataclass 定义
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import yaml
from pathlib import Path


@dataclass
class DeviceConfig:
    """设备配置"""
    port: str = 'COM1'
    baudrate: int = 115200


@dataclass
class TestConfig:
    """测试配置基类"""
    motor_port: str = 'COM1'
    motor_baudrate: int = 115200
    encoder_port: str = 'COM3'
    encoder_resolution: int = 4096
    laser_port: str = 'COM2'
    laser_precision: float = 0.0001
    rotation_speed: float = 100.0
    wait_stable_timeout: float = 0.5

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'TestConfig':
        """从 YAML 加载配置"""
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {yaml_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        devices = data.get('devices', {})
        kwargs = {}
        
        for dev in ['motor', 'encoder', 'laser']:
            if dev in devices:
                for key, value in devices[dev].items():
                    kwargs[f'{dev}_{key}'] = value
        
        return cls(**kwargs)
    
    def to_dict(self) -> dict:
        """转字典"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


@dataclass
class PrecisionTestConfig(TestConfig):
    """精度测试配置"""
    tolerance: float = 0.1
    test_angles: List[float] = field(default_factory=lambda: [0, 45, 90, 135, 180, 225, 270, 315])
    samples_per_angle: int = 5


@dataclass
class RepeatabilityTestConfig(TestConfig):
    """重复性测试配置"""
    tolerance: float = 0.05
    samples: int = 10


def get_config(config_class, yaml_path: Optional[str] = None, **overrides) -> TestConfig:
    """获取配置（加载 YAML + 参数覆盖）"""
    if yaml_path and Path(yaml_path).exists():
        config = config_class.from_yaml(yaml_path)
    else:
        config = config_class()
    
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config