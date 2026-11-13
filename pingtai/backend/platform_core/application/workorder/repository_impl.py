"""
工业自动化测试平台 - 工单仓储实现
WorkOrder Repository Implementation
"""
from typing import List, Optional
from sqlalchemy.orm import sessionmaker
from ...storage.models import WorkOrderModel
from .domain import WorkOrder, WorkOrderStatus
from .repository import IWorkOrderRepository


class WorkOrderRepository(IWorkOrderRepository):
    """工单仓储实现"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def _map_to_domain(self, workorder_model: WorkOrderModel) -> WorkOrder:
        """将ORM模型映射到领域模型"""
        return WorkOrder(
            workorder_id=workorder_model.workorder_id,
            product_model=workorder_model.product_model,
            batch_number=workorder_model.batch_number,
            planned_quantity=workorder_model.planned_quantity or 0,
            completed_quantity=workorder_model.completed_quantity or 0,
            ng_quantity=workorder_model.ng_quantity or 0,
            route_config=workorder_model.route_config,
            priority=workorder_model.priority or 0,
            status=WorkOrderStatus(workorder_model.status),
            start_time=workorder_model.start_time,
            end_time=workorder_model.end_time,
            created_at=workorder_model.created_at,
            updated_at=workorder_model.updated_at,
            version=workorder_model.version
        )
    
    def _map_to_model(self, workorder: WorkOrder) -> WorkOrderModel:
        """将领域模型映射到ORM模型"""
        return WorkOrderModel(
            workorder_id=workorder.workorder_id,
            product_model=workorder.product_model,
            batch_number=workorder.batch_number,
            planned_quantity=workorder.planned_quantity,
            completed_quantity=workorder.completed_quantity,
            ng_quantity=workorder.ng_quantity,
            route_config=workorder.route_config,
            priority=workorder.priority,
            status=workorder.status.value,
            start_time=workorder.start_time,
            end_time=workorder.end_time,
            created_at=workorder.created_at,
            updated_at=workorder.updated_at,
            version=workorder.version
        )
    
    def save(self, workorder: WorkOrder) -> WorkOrder:
        """保存工单"""
        with self.session_factory() as session:
            # 检查是否存在
            existing = session.query(WorkOrderModel).filter(
                WorkOrderModel.workorder_id == workorder.workorder_id
            ).first()
            
            if existing:
                # 更新现有记录
                existing.product_model = workorder.product_model
                existing.batch_number = workorder.batch_number
                existing.planned_quantity = workorder.planned_quantity
                existing.completed_quantity = workorder.completed_quantity
                existing.ng_quantity = workorder.ng_quantity
                existing.route_config = workorder.route_config
                existing.priority = workorder.priority
                existing.status = workorder.status.value
                existing.start_time = workorder.start_time
                existing.end_time = workorder.end_time
                existing.updated_at = workorder.updated_at
                existing.version = workorder.version
                
                session.commit()
                session.refresh(existing)
                return self._map_to_domain(existing)
            else:
                # 创建新记录
                model = self._map_to_model(workorder)
                session.add(model)
                session.commit()
                session.refresh(model)
                return self._map_to_domain(model)
    
    def find_by_id(self, workorder_id: str) -> Optional[WorkOrder]:
        """根据ID查找工单"""
        with self.session_factory() as session:
            workorder_model = session.query(WorkOrderModel).filter(
                WorkOrderModel.workorder_id == workorder_id
            ).first()
            
            if workorder_model:
                return self._map_to_domain(workorder_model)
            return None
    
    def find_by_status(self, status: str) -> List[WorkOrder]:
        """根据状态查找工单"""
        with self.session_factory() as session:
            workorder_models = session.query(WorkOrderModel).filter(
                WorkOrderModel.status == status
            ).all()
            
            return [self._map_to_domain(model) for model in workorder_models]
    
    def find_by_product_model(self, product_model: str) -> List[WorkOrder]:
        """根据产品型号查找工单"""
        with self.session_factory() as session:
            workorder_models = session.query(WorkOrderModel).filter(
                WorkOrderModel.product_model == product_model
            ).all()
            
            return [self._map_to_domain(model) for model in workorder_models]
    
    def find_active_workorders(self) -> List[WorkOrder]:
        """查找活跃工单"""
        with self.session_factory() as session:
            workorder_models = session.query(WorkOrderModel).filter(
                WorkOrderModel.status.in_(['PENDING', 'RUNNING', 'PAUSED'])
            ).all()
            
            return [self._map_to_domain(model) for model in workorder_models]