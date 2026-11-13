"""
工单领域服务 - 工业业务主链路
"""
from typing import List, Optional
from datetime import datetime, timedelta
from encoder_test.application.workorder.domain import WorkOrder, WorkOrderStatus
from encoder_test.application.workorder.repository import IWorkOrderRepository


class WorkOrderDomainService:
    """工单领域服务 - 处理工单间的业务逻辑"""
    
    def __init__(self, workorder_repository: IWorkOrderRepository):
        self._repository = workorder_repository
    
    def validate_workorder_creation(self, workorder_id: str, product_model: str) -> bool:
        """验证工单创建条件"""
        # 检查工单ID是否已存在
        existing = self._repository.find_by_id(workorder_id)
        if existing:
            raise ValueError(f"Workorder with ID {workorder_id} already exists")
        
        # 检查产品型号是否有效（这里只是简单示例，实际可能需要检查产品配置等）
        if not product_model or len(product_model.strip()) == 0:
            raise ValueError("Product model cannot be empty")
        
        return True
    
    def calculate_workorder_completion(self, workorder: WorkOrder) -> float:
        """计算工单完成百分比"""
        if workorder.planned_quantity <= 0:
            return 0.0
        
        completed = workorder.completed_quantity
        return min(completed / workorder.planned_quantity * 100, 100.0)
    
    def is_workorder_complete(self, workorder: WorkOrder) -> bool:
        """判断工单是否完成"""
        # 工单完成的条件：完成数量达到计划数量 或 状态已经是COMPLETED
        if workorder.status == WorkOrderStatus.COMPLETED:
            return True
        
        if workorder.planned_quantity > 0:
            return workorder.completed_quantity >= workorder.planned_quantity
        
        return False
    
    def get_workorder_yield_rate(self, workorder_id: str) -> float:
        """获取工单良率"""
        # 注意：这只是一个框架，实际实现需要查询相关报告数据
        # 在实际应用中，这里应该关联ReportQueryService来计算良率
        workorder = self._repository.find_by_id(workorder_id)
        if not workorder or workorder.completed_quantity <= 0:
            return 0.0
        
        # 简化的良率计算：(完成数量 - NG数量) / 完成数量
        if workorder.completed_quantity > 0:
            yield_rate = (workorder.completed_quantity - workorder.ng_quantity) / workorder.completed_quantity * 100
            return max(0.0, min(100.0, yield_rate))
        
        return 0.0
    
    def can_transition_status(self, current_status: WorkOrderStatus, target_status: WorkOrderStatus) -> bool:
        """检查工单状态转换是否合法"""
        valid_transitions = {
            WorkOrderStatus.PENDING: [WorkOrderStatus.RUNNING, WorkOrderStatus.CANCELLED],
            WorkOrderStatus.RUNNING: [WorkOrderStatus.PAUSED, WorkOrderStatus.COMPLETED, WorkOrderStatus.CANCELLED],
            WorkOrderStatus.PAUSED: [WorkOrderStatus.RUNNING, WorkOrderStatus.CANCELLED],
            WorkOrderStatus.COMPLETED: [],
            WorkOrderStatus.CANCELLED: []
        }
        
        return target_status in valid_transitions.get(current_status, [])
    
    def prioritize_workorders(self, workorders: List[WorkOrder]) -> List[WorkOrder]:
        """根据优先级排序工单"""
        # 排序规则：状态(运行中 > 待开始 > 暂停)，然后按优先级数值降序，最后按创建时间升序
        def sort_key(wo: WorkOrder):
            status_priority = {
                WorkOrderStatus.RUNNING: 3,
                WorkOrderStatus.PENDING: 2,
                WorkOrderStatus.PAUSED: 1,
                WorkOrderStatus.CANCELLED: 0,
                WorkOrderStatus.COMPLETED: 0
            }.get(wo.status, 0)
            
            return (-status_priority, -wo.priority, wo.created_at.timestamp())
        
        return sorted(workorders, key=sort_key)
    
    def get_workorder_efficiency(self, workorder_id: str) -> dict:
        """获取工单效率指标"""
        workorder = self._repository.find_by_id(workorder_id)
        if not workorder:
            return {"error": f"Workorder {workorder_id} not found"}
        
        completion_rate = self.calculate_workorder_completion(workorder)
        yield_rate = self.get_workorder_yield_rate(workorder_id)
        
        # 计算运行时间（如果有）
        duration_seconds = 0
        if workorder.start_time:
            end_time = workorder.end_time or datetime.now()
            duration_seconds = (end_time - workorder.start_time).total_seconds()
        
        return {
            "completion_rate": completion_rate,
            "yield_rate": yield_rate,
            "duration_seconds": duration_seconds,
            "efficiency_score": (completion_rate * yield_rate) / 100 if completion_rate > 0 else 0
        }


class WorkOrderBusinessRules:
    """工单业务规则"""
    
    @staticmethod
    def validate_quantity_update(old_quantity: int, new_quantity: int, max_allowed: int = None) -> bool:
        """验证数量更新是否合规"""
        if new_quantity < old_quantity:
            return False  # 数量不能减少
        
        if max_allowed is not None and new_quantity > max_allowed:
            return False  # 不能超过最大值
        
        return True
    
    @staticmethod
    def should_auto_complete(workorder: WorkOrder) -> bool:
        """判断是否应自动完成工单"""
        if workorder.status != WorkOrderStatus.RUNNING:
            return False
        
        if workorder.planned_quantity <= 0:
            return False  # 无限量工单不会自动完成
        
        return workorder.completed_quantity >= workorder.planned_quantity
    
    @staticmethod
    def calculate_eta(workorder: WorkOrder, throughput_per_hour: float = 10.0) -> Optional[datetime]:
        """计算预计完成时间"""
        if workorder.status != WorkOrderStatus.RUNNING or workorder.planned_quantity <= 0:
            return None
        
        remaining = workorder.planned_quantity - workorder.completed_quantity
        if remaining <= 0:
            return workorder.end_time or datetime.now()
        
        if throughput_per_hour <= 0:
            return None
        
        hours_remaining = remaining / throughput_per_hour
        current_time = datetime.now()
        estimated_completion = current_time + timedelta(hours=hours_remaining)
        
        return estimated_completion