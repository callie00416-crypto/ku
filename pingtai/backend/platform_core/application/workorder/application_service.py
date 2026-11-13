"""
工业自动化测试平台 - 工单应用服务
WorkOrder Application Service
"""
from typing import List
from .domain import WorkOrder, WorkOrderStatus
from .repository import IWorkOrderRepository


class WorkOrderApplicationService:
    """工单应用服务"""
    
    def __init__(self, workorder_repository: IWorkOrderRepository):
        self._repository = workorder_repository
    
    def create_workorder(self, 
                        workorder_id: str,
                        product_model: str,
                        batch_number: str = None,
                        planned_quantity: int = 0,
                        route_config: dict = None,
                        priority: int = 0) -> WorkOrder:
        """创建工单"""
        # 检查工单ID是否已存在
        existing = self._repository.find_by_id(workorder_id)
        if existing:
            raise ValueError(f"Workorder with ID {workorder_id} already exists")
        
        workorder = WorkOrder(
            workorder_id=workorder_id,
            product_model=product_model,
            batch_number=batch_number,
            planned_quantity=planned_quantity,
            route_config=route_config,
            priority=priority
        )
        
        return self._repository.save(workorder)
    
    def start_workorder(self, workorder_id: str) -> WorkOrder:
        """开始工单"""
        workorder = self._repository.find_by_id(workorder_id)
        if not workorder:
            raise ValueError(f"Workorder with ID {workorder_id} not found")
        
        workorder.start()
        return self._repository.save(workorder)
    
    def pause_workorder(self, workorder_id: str) -> WorkOrder:
        """暂停工单"""
        workorder = self._repository.find_by_id(workorder_id)
        if not workorder:
            raise ValueError(f"Workorder with ID {workorder_id} not found")
        
        workorder.pause()
        return self._repository.save(workorder)
    
    def resume_workorder(self, workorder_id: str) -> WorkOrder:
        """恢复工单"""
        workorder = self._repository.find_by_id(workorder_id)
        if not workorder:
            raise ValueError(f"Workorder with ID {workorder_id} not found")
        
        workorder.resume()
        return self._repository.save(workorder)
    
    def complete_workorder(self, workorder_id: str) -> WorkOrder:
        """完成工单"""
        workorder = self._repository.find_by_id(workorder_id)
        if not workorder:
            raise ValueError(f"Workorder with ID {workorder_id} not found")
        
        workorder.complete()
        return self._repository.save(workorder)
    
    def cancel_workorder(self, workorder_id: str) -> WorkOrder:
        """取消工单"""
        workorder = self._repository.find_by_id(workorder_id)
        if not workorder:
            raise ValueError(f"Workorder with ID {workorder_id} not found")
        
        workorder.cancel()
        return self._repository.save(workorder)
    
    def get_workorder(self, workorder_id: str) -> WorkOrder:
        """获取工单"""
        workorder = self._repository.find_by_id(workorder_id)
        if not workorder:
            raise ValueError(f"Workorder with ID {workorder_id} not found")
        
        return workorder
    
    def get_active_workorders(self) -> List[WorkOrder]:
        """获取活跃工单"""
        return self._repository.find_active_workorders()
    
    def get_workorders_by_status(self, status: WorkOrderStatus) -> List[WorkOrder]:
        """根据状态获取工单"""
        return self._repository.find_by_status(status.value)
    
    def get_workorders_by_product_model(self, product_model: str) -> List[WorkOrder]:
        """根据产品型号获取工单"""
        return self._repository.find_by_product_model(product_model)