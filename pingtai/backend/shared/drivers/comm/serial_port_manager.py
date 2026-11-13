"""
串口资源管理器 - Serial Port Resource Manager

【职责】
管理串口资源的分配和释放
检测串口占用情况
自动清理占用进程
提供串口资源池

【解决的问题】
1. 串口被重复打开导致权限错误
2. 串口资源泄漏
3. 串口占用检测
4. 自动清理占用进程

【工业应用】
工业自动化测试平台中，串口资源是有限的
需要统一管理，避免资源冲突
"""
import os
import sys
import time
import logging
import psutil
import threading
from typing import Dict, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class SerialPortStatus(Enum):
    """串口状态枚举"""
    FREE = "free"           # 空闲
    OCCUPIED = "occupied"   # 被占用
    ERROR = "error"         # 错误
    UNKNOWN = "unknown"     # 未知


@dataclass
class SerialPortInfo:
    """串口信息"""
    port: str
    status: SerialPortStatus
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    last_used: float = field(default_factory=time.time)
    lock_owner: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'port': self.port,
            'status': self.status.value,
            'process_id': self.process_id,
            'process_name': self.process_name,
            'last_used': self.last_used,
            'lock_owner': self.lock_owner
        }


class SerialPortManager:
    """串口资源管理器（单例模式）"""
    
    _instance: Optional['SerialPortManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._ports: Dict[str, SerialPortInfo] = {}
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()
        self._cleanup_interval = 300  # 5分钟清理一次
        self._port_timeout = 3600  # 1小时超时
        
        logger.info("串口资源管理器初始化完成")
        
        # 启动清理线程
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """启动清理线程"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(self._cleanup_interval)
                    self.cleanup_expired_ports()
                except Exception as e:
                    logger.error(f"清理线程异常: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("串口清理线程已启动")
    
    def get_port_lock(self, port: str) -> threading.Lock:
        """获取串口锁"""
        with self._global_lock:
            if port not in self._locks:
                self._locks[port] = threading.Lock()
            return self._locks[port]
    
    def check_port_status(self, port: str) -> SerialPortStatus:
        """检查串口状态
        
        Args:
            port: 串口名称（如 COM4, /dev/ttyUSB0）
            
        Returns:
            串口状态
        """
        try:
            # 尝试打开串口
            import serial
            test_serial = serial.Serial()
            test_serial.port = port
            test_serial.timeout = 0.1
            
            try:
                test_serial.open()
                test_serial.close()
                return SerialPortStatus.FREE
            except serial.SerialException as e:
                error_msg = str(e).lower()
                if 'permission denied' in error_msg or 'access is denied' in error_msg:
                    return SerialPortStatus.OCCUPIED
                elif 'could not open port' in error_msg or 'file not found' in error_msg:
                    return SerialPortStatus.ERROR
                else:
                    return SerialPortStatus.UNKNOWN
        except ImportError:
            logger.warning("serial 库未安装，无法检查串口状态")
            return SerialPortStatus.UNKNOWN
        except Exception as e:
            logger.error(f"检查串口状态异常: {e}")
            return SerialPortStatus.ERROR
    
    def find_occupying_process(self, port: str) -> Optional[tuple]:
        """查找占用串口的进程
        
        Args:
            port: 串口名称
            
        Returns:
            (进程ID, 进程名称) 或 None
        """
        try:
            port_lower = port.lower()
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()
                        if port_lower in cmdline_str:
                            return (proc.info['pid'], proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return None
        except Exception as e:
            logger.error(f"查找占用进程异常: {e}")
            return None
    
    def kill_occupying_process(self, port: str, force: bool = False) -> bool:
        """杀死占用串口的进程
        
        Args:
            port: 串口名称
            force: 是否强制杀死
            
        Returns:
            是否成功
        """
        occupying_process = self.find_occupying_process(port)
        if not occupying_process:
            logger.info(f"未找到占用串口 {port} 的进程")
            return True
        
        pid, name = occupying_process
        logger.info(f"找到占用串口 {port} 的进程: PID={pid}, Name={name}")
        
        try:
            if force:
                # 强制杀死进程
                proc = psutil.Process(pid)
                proc.kill()
                logger.info(f"已强制杀死进程: PID={pid}, Name={name}")
                time.sleep(0.5)  # 等待进程完全退出
                return True
            else:
                # 优雅终止进程
                proc = psutil.Process(pid)
                proc.terminate()
                logger.info(f"已终止进程: PID={pid}, Name={name}")
                
                # 等待进程退出
                try:
                    proc.wait(timeout=5)
                    return True
                except psutil.TimeoutExpired:
                    # 超时后强制杀死
                    proc.kill()
                    logger.warning(f"进程超时，强制杀死: PID={pid}, Name={name}")
                    time.sleep(0.5)
                    return True
        except psutil.NoSuchProcess:
            logger.info(f"进程已不存在: PID={pid}")
            return True
        except psutil.AccessDenied:
            logger.error(f"权限不足，无法终止进程: PID={pid}")
            return False
        except Exception as e:
            logger.error(f"终止进程异常: {e}")
            return False
    
    def acquire_port(self, port: str, owner: str = None, timeout: float = 10.0, 
                     auto_cleanup: bool = True) -> bool:
        """获取串口资源
        
        Args:
            port: 串口名称
            owner: 锁的拥有者标识
            timeout: 超时时间（秒）
            auto_cleanup: 是否自动清理占用进程
            
        Returns:
            是否成功获取
        """
        port_lock = self.get_port_lock(port)
        
        # 尝试获取锁
        acquired = port_lock.acquire(timeout=timeout)
        if not acquired:
            logger.error(f"获取串口 {port} 锁超时")
            return False
        
        try:
            # 检查串口状态
            status = self.check_port_status(port)
            
            if status == SerialPortStatus.OCCUPIED:
                logger.warning(f"串口 {port} 被占用")
                
                if auto_cleanup:
                    logger.info(f"尝试自动清理串口 {port}")
                    if self.kill_occupying_process(port, force=True):
                        time.sleep(1.0)  # 等待资源释放
                        status = self.check_port_status(port)
                
                if status == SerialPortStatus.OCCUPIED:
                    logger.error(f"串口 {port} 仍被占用，获取失败")
                    return False
            
            # 记录串口信息
            self._ports[port] = SerialPortInfo(
                port=port,
                status=SerialPortStatus.OCCUPIED,
                lock_owner=owner,
                last_used=time.time()
            )
            
            logger.info(f"成功获取串口 {port}")
            return True
            
        except Exception as e:
            logger.error(f"获取串口 {port} 异常: {e}")
            return False
    
    def release_port(self, port: str):
        """释放串口资源
        
        Args:
            port: 串口名称
        """
        try:
            # 移除串口信息
            if port in self._ports:
                del self._ports[port]
            
            # 释放锁
            if port in self._locks:
                self._locks[port].release()
            
            logger.info(f"已释放串口 {port}")
            
        except Exception as e:
            logger.error(f"释放串口 {port} 异常: {e}")
    
    def cleanup_expired_ports(self):
        """清理过期的串口资源"""
        current_time = time.time()
        expired_ports = []
        
        with self._global_lock:
            for port, info in list(self._ports.items()):
                if current_time - info.last_used > self._port_timeout:
                    expired_ports.append(port)
        
        for port in expired_ports:
            logger.info(f"清理过期串口: {port}")
            self.release_port(port)
    
    def get_all_ports_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有串口状态"""
        result = {}
        
        with self._global_lock:
            for port, info in self._ports.items():
                result[port] = info.to_dict()
        
        return result
    
    def reset_port(self, port: str) -> bool:
        """重置串口（强制释放）
        
        Args:
            port: 串口名称
            
        Returns:
            是否成功
        """
        try:
            logger.info(f"重置串口: {port}")
            
            # 杀死占用进程
            self.kill_occupying_process(port, force=True)
            time.sleep(1.0)
            
            # 释放资源
            self.release_port(port)
            
            # 验证串口状态
            status = self.check_port_status(port)
            if status == SerialPortStatus.FREE:
                logger.info(f"串口 {port} 重置成功")
                return True
            else:
                logger.error(f"串口 {port} 重置失败，状态: {status.value}")
                return False
                
        except Exception as e:
            logger.error(f"重置串口 {port} 异常: {e}")
            return False
    
    def list_available_ports(self) -> list:
        """列出可用的串口"""
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except ImportError:
            logger.warning("serial 库未安装，无法列出串口")
            return []
        except Exception as e:
            logger.error(f"列出串口异常: {e}")
            return []


# 全局单例
_serial_port_manager = None


def get_serial_port_manager() -> SerialPortManager:
    """获取串口资源管理器单例"""
    global _serial_port_manager
    if _serial_port_manager is None:
        _serial_port_manager = SerialPortManager()
    return _serial_port_manager


def acquire_serial_port(port: str, owner: str = None, timeout: float = 10.0, 
                        auto_cleanup: bool = True) -> bool:
    """获取串口资源（便捷函数）
    
    Args:
        port: 串口名称
        owner: 锁的拥有者标识
        timeout: 超时时间（秒）
        auto_cleanup: 是否自动清理占用进程
        
    Returns:
        是否成功获取
    """
    manager = get_serial_port_manager()
    return manager.acquire_port(port, owner, timeout, auto_cleanup)


def release_serial_port(port: str):
    """释放串口资源（便捷函数）
    
    Args:
        port: 串口名称
    """
    manager = get_serial_port_manager()
    manager.release_port(port)


def reset_serial_port(port: str) -> bool:
    """重置串口（便捷函数）
    
    Args:
        port: 串口名称
        
    Returns:
        是否成功
    """
    manager = get_serial_port_manager()
    return manager.reset_port(port)


if __name__ == '__main__':
    # 测试代码
    import serial
    
    print("=" * 60)
    print("串口资源管理器测试")
    print("=" * 60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    print("\n可用串口:")
    ports = manager.list_available_ports()
    for port in ports:
        print(f"  - {port}")
    
    if ports:
        test_port = ports[0]
        print(f"\n测试串口: {test_port}")
        
        # 检查串口状态
        status = manager.check_port_status(test_port)
        print(f"串口状态: {status.value}")
        
        # 获取串口
        print(f"\n获取串口...")
        if manager.acquire_port(test_port, owner="test", timeout=5.0):
            print("✅ 获取成功")
            
            # 尝试打开串口
            try:
                ser = serial.Serial(test_port, baudrate=9600, timeout=1.0)
                print(f"✅ 串口打开成功")
                ser.close()
            except Exception as e:
                print(f"❌ 串口打开失败: {e}")
            
            # 释放串口
            print(f"\n释放串口...")
            manager.release_port(test_port)
            print("✅ 释放成功")
        else:
            print("❌ 获取失败")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)