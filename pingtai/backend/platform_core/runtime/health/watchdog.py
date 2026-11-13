"""
看门狗 - 系统级监控和恢复
"""
import asyncio
import time
import logging
import signal
import sys
import threading
from datetime import datetime
from typing import Callable, Optional


class Watchdog:
    """看门狗 - 系统级监控和恢复"""
    
    def __init__(self, timeout: int = 300):  # 5分钟默认超时
        self.timeout = timeout
        self.last_kick_time = time.time()
        self.logger = logging.getLogger(__name__)
        self.watchdog_task = None
        self.emergency_callback: Optional[Callable] = None
        self.is_active = False
        
    def kick(self):
        """踢看门狗（喂狗）"""
        self.last_kit_time = time.time()
        # self.logger.debug("看门狗被喂食")
        
    def set_emergency_callback(self, callback: Callable):
        """设置紧急回调函数"""
        self.emergency_callback = callback
        
    async def start(self):
        """启动看门狗"""
        if self.is_active:
            return
            
        self.is_active = True
        self.watchdog_task = asyncio.create_task(self._watchdog_loop())
        self.logger.info(f"看门狗已启动，超时时间: {self.timeout}秒")
        
        # 注册信号处理器
        def signal_handler(signum, frame):
            self.logger.info(f"收到信号 {signum}，正在清理...")
            asyncio.create_task(self.stop())
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def _watchdog_loop(self):
        """看门狗监控循环"""
        while self.is_active:
            try:
                current_time = time.time()
                time_since_kick = current_time - self.last_kick_time
                
                if time_since_kick > self.timeout:
                    self.logger.critical(f"看门狗超时! 最后喂食时间: "
                                       f"{datetime.fromtimestamp(self.last_kick_time)}")
                    await self._emergency_procedure()
                    break
                    
                await asyncio.sleep(min(10, self.timeout / 10))  # 检查频率
            except asyncio.CancelledError:
                self.logger.info("看门狗任务被取消")
                break
            except Exception as e:
                self.logger.error(f"看门狗循环错误: {e}")
                await asyncio.sleep(5)
                
    async def _emergency_procedure(self):
        """紧急处理程序"""
        self.logger.critical("执行紧急处理程序...")
        
        if self.emergency_callback:
            try:
                await self.emergency_callback()
            except Exception as e:
                self.logger.error(f"紧急回调执行失败: {e}")
                
        # 记录系统状态
        self._log_system_state()
        
        # 退出系统
        self.logger.critical("系统即将退出...")
        sys.exit(1)
        
    def _log_system_state(self):
        """记录系统状态"""
        import psutil
        process = psutil.Process()
        
        self.logger.info(f"进程内存: {process.memory_info().rss / 1024 / 1024:.2f}MB")
        self.logger.info(f"CPU使用率: {process.cpu_percent()}%")
        self.logger.info(f"线程数: {process.num_threads()}")
        
    async def stop(self):
        """停止看门狗"""
        self.is_active = False
        if self.watchdog_task:
            self.watchdog_task.cancel()
            try:
                await self.watchdog_task
            except asyncio.CancelledError:
                pass
        self.logger.info("看门狗已停止")