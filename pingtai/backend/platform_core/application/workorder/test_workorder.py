"""
工单领域测试
"""
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..storage.models import Base, WorkOrderModel
from ..application.workorder.domain import WorkOrder, WorkOrderStatus
from ..application.workorder.repository_impl import WorkOrderRepository


class TestWorkOrder(unittest.TestCase):
    def setUp(self):
        # 创建内存数据库进行测试
        self.engine = create_engine('sqlite:///test.db')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建仓储实例
        self.repo = WorkOrderRepository(self.Session)
    
    def test_create_workorder(self):
        """测试创建工单"""
        workorder = WorkOrder(
            workorder_id="WO001",
            product_model="Product_A",
            planned_quantity=100,
            batch_number="BATCH001"
        )
        
        saved_workorder = self.repo.save(workorder)
        
        self.assertEqual(saved_workorder.workorder_id, "WO001")
        self.assertEqual(saved_workorder.product_model, "Product_A")
        self.assertEqual(saved_workorder.planned_quantity, 100)
        self.assertEqual(saved_workorder.status, WorkOrderStatus.PENDING)
    
    def test_workorder_lifecycle(self):
        """测试工单生命周期"""
        workorder = WorkOrder(
            workorder_id="WO002",
            product_model="Product_B",
            planned_quantity=50
        )
        
        # 保存初始状态
        workorder = self.repo.save(workorder)
        
        # 开始工单
        workorder.start()
        workorder = self.repo.save(workorder)
        self.assertEqual(workorder.status, WorkOrderStatus.RUNNING)
        self.assertIsNotNone(workorder.start_time)
        
        # 暂停工单
        workorder.pause()
        workorder = self.repo.save(workorder)
        self.assertEqual(workorder.status, WorkOrderStatus.PAUSED)
        
        # 恢复工单
        workorder.resume()
        workorder = self.repo.save(workorder)
        self.assertEqual(workorder.status, WorkOrderStatus.RUNNING)
        
        # 完成工单
        workorder.complete()
        workorder = self.repo.save(workorder)
        self.assertEqual(workorder.status, WorkOrderStatus.COMPLETED)
        self.assertIsNotNone(workorder.end_time)
    
    def test_increment_quantities(self):
        """测试增加数量"""
        workorder = WorkOrder(
            workorder_id="WO003",
            product_model="Product_C",
            planned_quantity=10
        )
        
        workorder = self.repo.save(workorder)
        
        # 增加完成数量
        workorder.increment_completed_quantity(5)
        workorder = self.repo.save(workorder)
        
        self.assertEqual(workorder.completed_quantity, 5)
        
        # 增加NG数量
        workorder.increment_ng_quantity(1)
        workorder = self.repo.save(workorder)
        
        self.assertEqual(workorder.ng_quantity, 1)
    
    def test_find_workorders(self):
        """测试查找工单"""
        # 创建多个工单
        wo1 = WorkOrder(
            workorder_id="WO004",
            product_model="Product_D",
            status=WorkOrderStatus.PENDING
        )
        wo2 = WorkOrder(
            workorder_id="WO005",
            product_model="Product_D",
            status=WorkOrderStatus.RUNNING
        )
        
        self.repo.save(wo1)
        self.repo.save(wo2)
        
        # 测试按产品型号查找
        found = self.repo.find_by_product_model("Product_D")
        self.assertEqual(len(found), 2)
        
        # 测试按状态查找
        pending_wos = self.repo.find_by_status("PENDING")
        self.assertEqual(len(pending_wos), 1)
        
        # 测试按ID查找
        found_wo = self.repo.find_by_id("WO004")
        self.assertIsNotNone(found_wo)
        self.assertEqual(found_wo.workorder_id, "WO004")
        
        # 测试查找活跃工单
        active_wos = self.repo.find_active_workorders()
        self.assertEqual(len(active_wos), 2)  # PENDING 和 RUNNING 都是活跃状态


if __name__ == '__main__':
    unittest.main()