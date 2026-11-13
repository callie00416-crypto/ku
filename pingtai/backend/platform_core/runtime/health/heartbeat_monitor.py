"""
心跳监控器
"""
import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Callable, Optional


class HeartbeatMonitor:
    """心跳监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.components = {}  # {component_id: last_heartbeat_time}
        self.heartbeat_callbacks = {}  # {component_id: callback_func}
        self.monitor_task = None
        self.check_interval = 30  # 检查间隔（秒）
        self.timeout_threshold = 60  # 超时阈值（秒）
        
    def register_component(self, component_id: str, callback: Optional[Callable] = None):
        """注册组件"""
        self.components[component_id] = time.time()
        if callback:
            self.heartbeat_callbacks[component_id] = callback
        self.logger.info(f"注册组件: {component_id}")
        
    def unregister_component(self, component_id: str):
        """注销组件"""
        if component_id in self.components:
            del self.components[component_id]
        if component_id in self.heartbeat_callbacks:
            del self.heartbeat_callbacks[component_id]
        self.logger.info(f"注销组件: {component_id}")
        
    def heartbeat(self, component_id: str):
        """组件心跳"""
        if component_id in self.components:
            self.components[component_id] = time.time()
            # self.logger.debug(f"组件心跳: {component_id}")
        else:
            self.logger.warning(f"未知组件心跳: {component_id}")
            
    async def start_monitoring(self):
        """开始监控"""
        if self.monitor_task:
            return
            
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info("心跳监控已启动")
        
    async def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                await self._check_heartbeats()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                self.logger.info("心跳监控已取消")
                break
            except Exception as e:
                self.logger.error(f"心跳监控错误: {e}")
                
    async def _check_heartbeats(self):
        """检查心跳"""
        current_time = time.time()
        dead_components = []
        
        for component_id, last_heartbeat in self.components.items():
            if current_time - last_heartbeat > self.timeout_threshold:
                dead_components.append(component_id)
                self.logger.error(f"组件心跳超时: {component_id}, "
                                f"最后心跳: {datetime.fromtimestamp(last_heartbeat)}")
                                
        # 处理死亡组件
        for component_id in dead_components:
            await self._handle_dead_component(component_id)
            
    async def _handle_dead_component(self, component_id: str):
        """处理死亡组件"""
        # 调用回调函数（如果存在）
        if component_id in self.heartbeat_callbacks:
            try:
                callback = self.heartbeat_callbacks[component_id]
                await callback(component_id, 'timeout')
            except Exception as e:
                self.logger.error(f"处理死亡组件回调错误: {e}")
                
    def stop_monitoring(self):
        """停止监控"""
        if self.monitor_task:
            self.monitor_task.cancel()
            self.monitor_task = None