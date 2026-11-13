"""
驱动管理器 - 统一管理所有驱动，支持热插拔、断线重连、心跳检测
支持 Mock 驱动与真实驱动无缝切换

【架构】
DriverManager - 统一管理所有驱动
职责：
- 驱动生命周期管理
- 心跳检测与故障恢复
- Mock/真实驱动切换
- 配置管理与加载
"""
import time
import json
import logging
import threading
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from shared.drivers.base.base_comm import BaseComm
from shared.drivers.base.base_protocol import BaseProtocol
from shared.drivers.base.base_device import BaseDevice
from projects.encoder_test.drivers.factory.driver_factory import DriverFactory

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path:
            # 默认配置
            return {
                'mock': {
                    'enabled': True,
                    'serial_port': 'COM3',
                    'serial_baudrate': 9600,
                    'serial_mode': 'normal',
                    'can_channel': 'can0',
                    'can_bitrate': 500000,
                    'can_mode': 'normal',
                    'modbus_slave_id': 1,
                    'modbus_mode': 'rtu',
                    'encoder_resolution': 4096,
                    'encoder_mode': 'normal',
                    'motor_mode': 'normal'
                },
                'comm': {
                    'rs485': {
                        'port': 'COM3',
                        'baudrate': 9600
                    },
                    'tcp': {
                        'host': 'localhost',
                        'port': 502
                    },
                    'can': {
                        'channel': 'can0',
                        'bitrate': 500000
                    }
                },
                'protocol': {
                    'modbus': {
                        'comm_driver': 'rs485',
                        'slave_id': 1
                    }
                },
                'device': {
                    'encoder': {
                        'protocol_driver': 'modbus',
                        'resolution': 4096
                    },
                    'motor': {
                        'protocol_driver': 'modbus',
                        'node_id': 1
                    }
                }
            }
        
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"配置文件不存在: {self.config_path}")
                return self._load_config()  # 返回默认配置
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._load_config()  # 返回默认配置
    
    def get(self, key: str, default=None):
        """
        获取配置值（支持点号分隔的嵌套键）
        
        Args:
            key: 配置键，如 'mock.enabled'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """获取全部配置"""
        return self._config


class DriverStatus:
    """驱动状态枚举"""
    INIT = 'init'
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    FAULT = 'fault'
    BUSY = 'busy'


class DriverManager:
    """驱动管理器 - 统一管理所有驱动"""
    
    def __init__(self, config_path: str = None, enable_heartbeat: bool = True,
                 heartbeat_interval: float = 5.0):
        """
        初始化驱动管理器
        
        Args:
            config_path: 配置文件路径
            enable_heartbeat: 是否启用心跳检测
            heartbeat_interval: 心跳检测间隔（秒）
        """
        self.config_loader = ConfigLoader(config_path)
        self.mock_enabled = self.config_loader.get('mock.enabled', False)
        self.enable_heartbeat = enable_heartbeat
        self.heartbeat_interval = heartbeat_interval
        
        # 驱动实例字典
        self.drivers: Dict[str, Union[BaseComm, BaseProtocol, BaseDevice]] = {}
        
        # 心跳检测线程
        self._heartbeat_thread = None
        self._heartbeat_running = False
        
        # 初始化驱动
        self._init_drivers()
        
        # 启动心跳检测
        if self.enable_heartbeat:
            self.start_heartbeat()
    
    def _init_drivers(self):
        """初始化所有驱动"""
        self.drivers.clear()
        
        # 使用驱动工厂创建驱动
        self.drivers = DriverFactory.create_drivers_from_config(
            config=self.config_loader.get_all(),
            mock_mode=self.mock_enabled
        )
        
        logger.info(f"驱动初始化完成 (Mock模式: {self.mock_enabled}, 驱动数量: {len(self.drivers)})")
    
    def connect_all(self) -> bool:
        """连接所有驱动"""
        success = True
        for name, driver in self.drivers.items():
            try:
                if hasattr(driver, 'connect'):
                    if not driver.connect():
                        logger.warning(f"驱动连接失败: {name}")
                        success = False
                elif hasattr(driver, 'open'):
                    if not driver.open():
                        logger.warning(f"驱动打开失败: {name}")
                        success = False
            except Exception as e:
                logger.error(f"驱动 {name} 连接异常: {e}")
                success = False
        return success
    
    def disconnect_all(self):
        """断开所有驱动"""
        for name, driver in self.drivers.items():
            try:
                if hasattr(driver, 'disconnect'):
                    driver.disconnect()
                elif hasattr(driver, 'close'):
                    driver.close()
            except Exception as e:
                logger.error(f"驱动 {name} 断开异常: {e}")
    
    def get_driver(self, name: str) -> Optional[Union[BaseComm, BaseProtocol, BaseDevice]]:
        """
        获取指定驱动
        
        Args:
            name: 驱动名称
            
        Returns:
            驱动实例
        """
        return self.drivers.get(name)
    
    def reconnect_driver(self, name: str) -> bool:
        """
        重连指定驱动
        
        Args:
            name: 驱动名称
            
        Returns:
            重连是否成功
        """
        driver = self.drivers.get(name)
        if not driver:
            logger.error(f"驱动不存在: {name}")
            return False
        
        # 尝试断开再重新连接
        try:
            if hasattr(driver, 'disconnect'):
                driver.disconnect()
            elif hasattr(driver, 'close'):
                driver.close()
        except Exception as e:
            logger.warning(f"驱动 {name} 断开时出错: {e}")
        
        try:
            if hasattr(driver, 'connect'):
                return driver.connect()
            elif hasattr(driver, 'open'):
                return driver.open()
        except Exception as e:
            logger.error(f"驱动 {name} 重连失败: {e}")
            return False
        
        return False
    
    def get_all_status(self) -> Dict[str, Any]:
        """获取所有驱动状态"""
        status = {'mock_enabled': self.mock_enabled}
        for name, driver in self.drivers.items():
            try:
                if hasattr(driver, 'health_check'):
                    status[name] = driver.health_check()
                else:
                    # 如果没有健康检查方法，则返回基本信息
                    status[name] = {
                        'status': getattr(driver, 'status', 'unknown'),
                        'is_connected': getattr(driver, 'is_connected', lambda: False)() if hasattr(driver, 'is_connected') else getattr(driver, 'is_open', False),
                        'driver_type': type(driver).__name__
                    }
            except Exception as e:
                status[name] = {'error': str(e)}
        return status
    
    def get_fault_drivers(self) -> List[str]:
        """获取故障驱动列表"""
        faults = []
        for name, driver in self.drivers.items():
            try:
                if hasattr(driver, 'health_check'):
                    health = driver.health_check()
                    if health.get('status') == DriverStatus.FAULT or not health.get('is_connected', True):
                        faults.append(name)
                else:
                    # 如果没有健康检查方法，检查连接状态
                    is_connected = getattr(driver, 'is_connected', lambda: False)() if hasattr(driver, 'is_connected') else getattr(driver, 'is_open', False)
                    if not is_connected:
                        faults.append(name)
            except Exception:
                # 如果检查状态时出错，也认为是故障
                faults.append(name)
        return faults
    
    def set_mock_mode(self, enabled: bool):
        """
        切换 Mock 模式
        
        Args:
            enabled: 是否启用 Mock 模式
        """
        if self.mock_enabled == enabled:
            return
        
        logger.info(f"切换驱动模式: {'Mock' if enabled else '真实'}")
        self.disconnect_all()
        self.mock_enabled = enabled
        self._init_drivers()
    
    def start_heartbeat(self):
        """启动心跳检测线程"""
        if self._heartbeat_running:
            return
        
        self._heartbeat_running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        logger.info("心跳检测已启动")
    
    def stop_heartbeat(self):
        """停止心跳检测"""
        self._heartbeat_running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2.0)
        logger.info("心跳检测已停止")
    
    def _heartbeat_loop(self):
        """心跳检测循环"""
        while self._heartbeat_running:
            try:
                for name, driver in self.drivers.items():
                    try:
                        # 检查驱动是否响应
                        if hasattr(driver, 'health_check'):
                            health = driver.health_check()
                            
                            # 检查连接状态
                            is_connected = health.get('is_connected', False)
                            if not is_connected:
                                logger.warning(f"驱动连接丢失: {name}")
                                
                                # 尝试重连
                                if self.reconnect_driver(name):
                                    logger.info(f"驱动 {name} 重连成功")
                                else:
                                    logger.error(f"驱动 {name} 重连失败")
                        else:
                            # 如果没有健康检查方法，检查连接状态
                            if hasattr(driver, 'is_connected'):
                                connected = driver.is_connected()
                            elif hasattr(driver, 'is_open'):
                                connected = driver.is_open
                            else:
                                connected = True  # 假设默认连接
                            
                            if not connected:
                                logger.warning(f"驱动连接丢失: {name}")
                                if self.reconnect_driver(name):
                                    logger.info(f"驱动 {name} 重连成功")
                                else:
                                    logger.error(f"驱动 {name} 重连失败")
                    except Exception as e:
                        logger.error(f"驱动 {name} 心跳检测异常: {e}")
            except Exception as e:
                logger.error(f"心跳检测循环异常: {e}")
            
            time.sleep(self.heartbeat_interval)
    
    def close(self):
        """关闭驱动管理器"""
        self.stop_heartbeat()
        self.disconnect_all()
        logger.info("驱动管理器已关闭")


# 全局驱动管理器实例
driver_manager = None


def get_driver_manager(config_path: str = None) -> DriverManager:
    """
    获取驱动管理器实例（单例模式）
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        驱动管理器实例
    """
    global driver_manager
    if driver_manager is None:
        driver_manager = DriverManager(config_path)
    return driver_manager