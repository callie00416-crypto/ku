"""
运行时指标收集器
"""
import time
import threading
from datetime import datetime
from typing import Dict, Any, List
import asyncio
import logging
from dataclasses import dataclass


@dataclass
class MetricPoint:
    """指标点"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = None


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self.metrics_lock = threading.Lock()
        self.retention_period = 3600 * 24  # 保留24小时的数据
        self.max_points_per_metric = 10000  # 每个指标最多保留10000个点
        
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录指标"""
        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        
        with self.metrics_lock:
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(metric_point)
            
            # 清理过期数据
            self._cleanup_expired_metrics(name)
            
    def _cleanup_expired_metrics(self, name: str):
        """清理过期指标数据"""
        current_time = time.time()
        cutoff_time = current_time - self.retention_period
        
        # 按时间过滤
        self.metrics[name] = [
            mp for mp in self.metrics[name]
            if mp.timestamp >= cutoff_time
        ]
        
        # 如果仍然太多，按数量截断
        if len(self.metrics[name]) > self.max_points_per_metric:
            self.metrics[name] = self.metrics[name][-self.max_points_per_metric:]
            
    def get_metric_values(self, name: str, since: float = None) -> List[MetricPoint]:
        """获取指标值"""
        with self.metrics_lock:
            if name not in self.metrics:
                return []
                
            if since is None:
                return self.metrics[name].copy()
            else:
                return [mp for mp in self.metrics[name] if mp.timestamp >= since]
                
    def get_aggregated_metrics(self, name: str, window_seconds: int = 300) -> Dict[str, float]:
        """获取聚合指标（5分钟窗口）"""
        current_time = time.time()
        since = current_time - window_seconds
        
        values = self.get_metric_values(name, since)
        if not values:
            return {}
            
        values_list = [mp.value for mp in values]
        return {
            'count': len(values_list),
            'avg': sum(values_list) / len(values_list),
            'min': min(values_list),
            'max': max(values_list),
            'last': values_list[-1] if values_list else 0
        }
        
    def get_all_metric_names(self) -> List[str]:
        """获取所有指标名称"""
        with self.metrics_lock:
            return list(self.metrics.keys())
            
    def get_current_values(self) -> Dict[str, float]:
        """获取所有指标的当前值"""
        current_values = {}
        with self.metrics_lock:
            for name, points in self.metrics.items():
                if points:
                    current_values[name] = points[-1].value
        return current_values