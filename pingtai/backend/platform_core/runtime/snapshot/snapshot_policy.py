"""
快照策略 - 定义哪些状态可以快照，哪些不可以
"""
from typing import Dict, Any, Set
import logging


class SnapshotPolicy:
    """快照策略 - 定义哪些状态可以快照，哪些不可以"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 允许快照的状态类型（关键运行时状态）
        self.ALLOWED_SNAPSHOT_STATES = {
            'running_tasks',
            'actor_states', 
            'device_connection_states',
            'current_workorder',
            'runtime_context',
            'pending_critical_events'
        }
        
        # 禁止快照的状态类型（避免快照膨胀）
        self.FORBIDDEN_SNAPSHOT_STATES = {
            'historical_events',
            'full_eventbus',
            'temporary_cache',
            'metrics_history',
            'completed_tasks',
            'large_objects',
            'waveform_data',
            'report_details'
        }
        
    def should_snapshot(self, state_type: str, data: Any = None) -> bool:
        """判断是否应该对特定状态进行快照"""
        # 检查是否在禁止列表中
        if state_type.lower() in self.FORBIDDEN_SNAPSHOT_STATES:
            self.logger.debug(f"状态类型 {state_type} 在禁止快照列表中")
            return False
            
        # 检查是否在允许列表中
        if state_type.lower() in self.ALLOWED_SNAPSHOT_STATES:
            # 对于允许的类型，进一步检查数据大小
            if data and self._is_data_too_large(data):
                self.logger.warning(f"状态类型 {state_type} 数据过大，跳过快照")
                return False
            return True
            
        # 默认情况下，不允许快照（安全默认值）
        self.logger.debug(f"状态类型 {state_type} 不在允许列表中，默认不允许快照")
        return False
        
    def _is_data_too_large(self, data: Any, threshold_mb: float = 10.0) -> bool:
        """检查数据是否过大（以MB为单位）"""
        try:
            import sys
            size_bytes = sys.getsizeof(str(data))
            size_mb = size_bytes / (1024 * 1024)
            return size_mb > threshold_mb
        except:
            # 如果无法计算大小，假设数据不大
            return False
            
    def validate_snapshot_content(self, snapshot_data: Dict[str, Any]) -> bool:
        """验证快照内容是否符合策略"""
        for key, value in snapshot_data.items():
            if not self.should_snapshot(key, value):
                self.logger.error(f"快照内容验证失败: {key} 不应该被快照")
                return False
        return True