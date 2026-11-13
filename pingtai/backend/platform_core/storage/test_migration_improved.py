"""
数据库迁移测试脚本（改进版）
"""
import os
import tempfile
from encoder_test.storage.migration_manager import DatabaseMigrationManager


def test_database_migration():
    """测试数据库迁移功能"""
    # 创建临时数据库文件进行测试
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
    
    try:
        # 创建迁移管理器
        print("创建数据库迁移管理器...")
        db_manager = DatabaseMigrationManager(f"sqlite:///{temp_db_path}")
        
        # 执行数据库迁移
        print("执行数据库迁移...")
        db_manager.alembic_upgrade("head")
        
        # 验证表是否创建成功
        print("验证数据库表是否创建成功...")
        from sqlalchemy import inspect
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'work_orders', 'tasks', 'stations', 'devices', 
            'alarms', 'reports', 'test_records', 'report_attachments'
        ]
        
        print(f"数据库中找到的表: {tables}")
        
        for table in expected_tables:
            if table in tables:
                print(f"✓ 表 '{table}' 创建成功")
            else:
                print(f"✗ 表 '{table}' 创建失败")
        
        # 测试插入一些数据
        print("\n测试数据插入...")
        from encoder_test.storage.models import WorkOrderModel
        from datetime import datetime
        
        with db_manager.get_session() as session:
            # 创建一个测试工单
            workorder = WorkOrderModel(
                workorder_id="TEST_WO001",
                product_model="Test_Product",
                planned_quantity=100,
                status="PENDING",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            session.add(workorder)
            session.commit()
            
            # 查询刚插入的数据
            retrieved = session.query(WorkOrderModel).filter(
                WorkOrderModel.workorder_id == "TEST_WO001"
            ).first()
            
            if retrieved:
                print(f"✓ 成功插入并查询工单: {retrieved.workorder_id}")
            else:
                print("✗ 数据插入/查询测试失败")
        
        print("\n数据库迁移测试完成!")
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理临时文件 - 在Windows上需要先关闭文件描述符
        try:
            os.close(temp_db_fd)
        except:
            pass  # 如果已经关闭则忽略错误
        
        try:
            os.unlink(temp_db_path)
        except PermissionError:
            # 在Windows上，如果数据库连接未完全关闭，可能会出现权限错误
            # 这通常是因为SQLite文件锁未释放
            print(f"警告: 无法删除临时数据库文件 {temp_db_path}，可能是因为文件仍被锁定")
            pass


if __name__ == "__main__":
    success = test_database_migration()
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败！")