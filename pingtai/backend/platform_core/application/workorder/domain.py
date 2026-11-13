"""
工业自动化测试平台 - 工单领域
WorkOrder Domain for Industrial Business Main Link
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class WorkOrderStatus(Enum):
    """工单状态枚举"""
    PENDING = "PENDING"  # 待开始
    RUNNING = "RUNNING"  # 运行中
    PAUSED = "PAUSED"    # 暂停
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消


@dataclass
class WorkOrder:
    """工单聚合根 - 工业业务主链路"""
    workorder_id: str
    product_model: str
    batch_number: Optional[str] = None
    planned_quantity: int = 0
    completed_quantity: int = 0
    ng_quantity: int = 0
    route_config: Optional[Dict[str, Any]] = None  # 工艺路线配置
    priority: int = 0
    status: WorkOrderStatus = WorkOrderStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    version: int = 0
    
    def start(self):
        """开始工单"""
        if self.status != WorkOrderStatus.PENDING:
            raise ValueError(f"Cannot start workorder in status {self.status.value}")
        
        self.status = WorkOrderStatus.RUNNING
        self.start_time = datetime.now()
        self.updated_at = datetime.now()
        self.version += 1
    
    def pause(self):
        """暂停工单"""
        if self.status != WorkOrderStatus.RUNNING:
            raise ValueError(f"Cannot pause workorder in status {self.status.value}")
        
        self.status = WorkOrderStatus.PAUSED
        self.updated_at = datetime.now()
        self.version += 1
    
    def resume(self):
        """恢复工单"""
        if self.status != WorkOrderStatus.PAUSED:
            raise ValueError(f"Cannot resume workorder in status {self.status.value}")
        
        self.status = WorkOrderStatus.RUNNING
        self.updated_at = datetime.now()
        self.version += 1
    
    def complete(self):
        """完成工单"""
        if self.status not in [WorkOrderStatus.RUNNING, WorkOrderStatus.PAUSED]:
            raise ValueError(f"Cannot complete workorder in status {self.status.value}")
        
        self.status = WorkOrderStatus.COMPLETED
        self.end_time = datetime.now()
        self.updated_at = datetime.now()
        self.version += 1
    
    def cancel(self):
        """取消工单"""
        if self.status in [WorkOrderStatus.COMPLETED, WorkOrderStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel workorder in status {self.status.value}")
        
        self.status = WorkOrderStatus.CANCELLED
        self.end_time = datetime.now()
        self.updated_at = datetime.now()
        self.version += 1
    
    def increment_completed_quantity(self, quantity: int = 1):
        """增加完成数量"""
        self.completed_quantity += quantity
        self.updated_at = datetime.now()
        self.version += 1
        
        # 如果完成数量达到计划数量，则自动完成工单
        if self.completed_quantity >= self.planned_quantity and self.status == WorkOrderStatus.RUNNING:
            if self.planned_quantity > 0:
                self.complete()
    
    def increment_ng_quantity(self, quantity: int = 1):
        """增加不良品数量"""
        self.ng_quantity += quantity
        self.updated_at = datetime.now()
        self.version += 1