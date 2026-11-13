"""
运行时健康监控系统
"""
import asyncio
import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import threading


@dataclass
class HealthMetrics:
    """健康指标"""
    timestamp: datetime
    actor_queue_size: int
    actor_processing_delay: float
    tick_delay: float
    event_lag: float
    db_write_delay: float
    memory_usage_mb: float
    reconnect_count: int
    task_timeout_count: int
    cpu_percent: float
    network_io: Dict[str, float]


class HealthMonitor:
    """健康监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        self.is_monitoring = False
        self.monitoring_thread = None
        self.system_metrics = {}
        
    async def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.logger.info("开始健康监控")
        
        # 在单独线程中运行监控
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self._collect_current_metrics()
                self.metrics_history.append(metrics)
                
                # 保留最近1000条记录
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                    
                # 检查是否存在问题
                self._check_health_issues(metrics)
                
                time.sleep(1)  # 每秒收集一次指标
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                
    def _collect_current_metrics(self) -> HealthMetrics:
        """收集当前指标"""
        process = psutil.Process()
        
        return HealthMetrics(
            timestamp=datetime.now(),
            actor_queue_size=0,  # 这里需要从实际的Actor系统获取
            actor_processing_delay=0.0,
            tick_delay=0.0,
            event_lag=0.0,
            db_write_delay=0.0,
            memory_usage_mb=process.memory_info().rss / 1024 / 1024,
            reconnect_count=0,  # 需要从连接管理器获取
            task_timeout_count=0,  # 需要从任务管理器获取
            cpu_percent=process.cpu_percent(),
            network_io={
                'bytes_sent': 0,
                'bytes_recv': 0
            }
        )
        
    def _check_health_issues(self, metrics: HealthMetrics):
        """检查健康问题"""
        issues = []
        
        # 检查内存使用
        if metrics.memory_usage_mb > 1000:  # 超过1GB
            issues.append(f"内存使用过高: {metrics.memory_usage_mb:.2f}MB")
            
        # 检查CPU使用
        if metrics.cpu_percent > 80:
            issues.append(f"CPU使用率过高: {metrics.cpu_percent}%")
            
        if issues:
            for issue in issues:
                self.logger.warning(f"健康问题: {issue}")
                
    async def get_current_health(self) -> HealthMetrics:
        """获取当前健康状态"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return self._collect_current_metrics()
        
    async def get_health_trend(self, minutes: int = 5) -> list:
        """获取健康趋势"""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp.timestamp() >= cutoff_time
        ]
        return recent_metrics
        
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)