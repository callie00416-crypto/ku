"""
RS485 串口驱动 - 通讯层实现

【架构】
RS485Driver(BaseComm)  - 物理通道

【改进】
- 集成串口资源管理器
- 自动处理串口占用问题
- 支持自动清理占用进程
- 提供完善的异常处理
"""
import time
import logging
from typing import Optional, Dict, Any, Callable
from ..base.base_comm import BaseComm

logger = logging.getLogger(__name__)


class RS485Comm(BaseComm):
    """RS485 串口通讯驱动（集成资源管理）"""
    
    def __init__(self, driver_id: str = 'rs485', port: str = 'COM3', baudrate: int = 9600,
                 parity: str = 'N', stopbits: float = 1.0, bytesize: int = 8, 
                 serial_factory: Callable = None, **kwargs):
        super().__init__(driver_id, port, baudrate, **kwargs)
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = kwargs.get('timeout', 1.0)
        self._serial = None
        self._reconnect_attempts = 0
        self._serial_factory = serial_factory
        self._port_acquired = False
        
        # 串口资源管理
        self._auto_cleanup = kwargs.get('auto_cleanup', True)
        self._acquire_timeout = kwargs.get('acquire_timeout', 10.0)
        
        if self._serial_factory is None:
            try:
                import serial
                self._serial_factory = serial
            except ImportError:
                logger.warning("serial 库未安装")
    
    def _acquire_port(self) -> bool:
        """获取串口资源"""
        try:
            from .serial_port_manager import get_serial_port_manager
            
            manager = get_serial_port_manager()
            return manager.acquire_port(
                self.port,
                owner=self.driver_id,
                timeout=self._acquire_timeout,
                auto_cleanup=self._auto_cleanup
            )
        except ImportError:
            logger.warning("串口资源管理器不可用，跳过资源获取")
            return True
        except Exception as e:
            logger.error(f"获取串口资源异常: {e}")
            return False
    
    def _release_port(self):
        """释放串口资源"""
        try:
            if self._port_acquired:
                from .serial_port_manager import get_serial_port_manager
                
                manager = get_serial_port_manager()
                manager.release_port(self.port)
                self._port_acquired = False
        except ImportError:
            logger.warning("串口资源管理器不可用，跳过资源释放")
        except Exception as e:
            logger.error(f"释放串口资源异常: {e}")
    
    def open(self) -> bool:
        """打开串口（集成资源管理）"""
        try:
            # 先获取串口资源
            if not self._acquire_port():
                logger.error(f"无法获取串口资源: {self.port}")
                return False
            
            self._port_acquired = True
            
            # 尝试打开串口
            try:
                self._serial = self._serial_factory.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    parity=self.parity,
                    stopbits=self.stopbits,
                    bytesize=self.bytesize,
                    timeout=self.timeout
                )
                self._is_open = True
                self.reset_error()
                self._reconnect_attempts = 0
                logger.info(f"RS485 打开成功: {self.port}")
                return True
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # 处理权限错误
                if 'permission denied' in error_msg or 'access is denied' in error_msg:
                    logger.warning(f"串口 {self.port} 权限错误，尝试清理占用进程")
                    
                    # 尝试重置串口
                    try:
                        from .serial_port_manager import get_serial_port_manager
                        manager = get_serial_port_manager()
                        
                        if manager.reset_port(self.port):
                            logger.info(f"串口 {self.port} 重置成功，重新尝试打开")
                            
                            # 重新尝试打开
                            self._serial = self._serial_factory.Serial(
                                port=self.port,
                                baudrate=self.baudrate,
                                parity=self.parity,
                                stopbits=self.stopbits,
                                bytesize=self.bytesize,
                                timeout=self.timeout
                            )
                            self._is_open = True
                            self.reset_error()
                            self._reconnect_attempts = 0
                            logger.info(f"RS485 打开成功: {self.port}")
                            return True
                        else:
                            logger.error(f"串口 {self.port} 重置失败")
                            return False
                    except Exception as reset_error:
                        logger.error(f"重置串口异常: {reset_error}")
                        return False
                
                # 其他错误
                logger.error(f"RS485 打开失败: {e}")
                self._is_open = False
                self.increment_error()
                return False
                
        except Exception as e:
            logger.error(f"RS485 打开异常: {e}")
            self._is_open = False
            self._release_port()
            self.increment_error()
            return False

    def connect(self) -> bool:
        """连接（与 open 同义，为了兼容协议层接口）"""
        return self.open()
    
    def disconnect(self):
        """断开连接（与 close 同义，为了兼容协议层接口）"""
        self.close()
    
    def close(self):
        """关闭串口（集成资源管理）"""
        try:
            if self._serial and self._serial.is_open:
                try:
                    self._serial.close()
                except Exception as e:
                    logger.error(f"RS485 关闭失败: {e}")
        except Exception as e:
            logger.error(f"关闭串口异常: {e}")
        finally:
            self._serial = None
            self._is_open = False
            self._release_port()
            logger.info(f"RS485 已关闭: {self.port}")

    def send(self, data: bytes) -> int:
        """发送数据"""
        if not self._is_open:
            raise ConnectionError("RS485 未打开")
        try:
            bytes_sent = self._serial.write(data)
            self._serial.flush()
            self.reset_error()
            return bytes_sent
        except Exception as e:
            logger.error(f"RS485 发送失败: {e}")
            self.increment_error()
            raise

    def recv(self, size: int = 1, timeout: float = 1.0) -> Optional[bytes]:
        """接收数据"""
        if not self._is_open:
            raise ConnectionError("RS485 未打开")
        try:
            self._serial.timeout = timeout
            data = self._serial.read(size)
            self.reset_error()
            return data if data else None
        except Exception as e:
            logger.error(f"RS485 接收失败: {e}")
            self.increment_error()
            raise

    def reconnect(self) -> bool:
        """重连串口（集成资源管理）"""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            logger.error(f"RS485 重连失败，已达最大次数")
            return False
        
        self._reconnect_attempts += 1
        logger.info(f"RS485 重连尝试 {self._reconnect_attempts}/{self._max_reconnect_attempts}")
        
        # 先关闭
        self.close()
        
        # 等待一段时间
        time.sleep(1.0)
        
        # 重新打开
        return self.open()

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        base = super().health_check()
        base.update({
            'driver_type': 'rs485',
            'port_acquired': self._port_acquired,
            'auto_cleanup': self._auto_cleanup,
        })
        return base