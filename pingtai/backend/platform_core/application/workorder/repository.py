"""
工业自动化测试平台 - 工单仓储接口
WorkOrder Repository Interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .domain import WorkOrder


class IWorkOrderRepository(ABC):
    """工单仓储接口"""
    
    @abstractmethod
    def save(self, workorder: WorkOrder) -> WorkOrder:
        """保存工单"""
        pass
    
    @abstractmethod
    def find_by_id(self, workorder_id: str) -> Optional[WorkOrder]:
        """根据ID查找工单"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[WorkOrder]:
        """根据状态查找工单"""
        pass
    
    @abstractmethod
    def find_by_product_model(self, product_model: str) -> List[WorkOrder]:
        """根据产品型号查找工单"""
        pass
    
    @abstractmethod
    def find_active_workorders(self) -> List[WorkOrder]:
        """查找活跃工单"""
        pass