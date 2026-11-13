"""
数据库迁移管理器
用于工业自动化测试平台的数据库迁移管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
import os
from pathlib import Path
from encoder_test.storage.models import Base


class DatabaseMigrationManager:
    """数据库迁移管理器"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # 配置Alembic
        alembic_dir = Path(__file__).parent / "migrations"
        self.alembic_cfg = Config()
        self.alembic_cfg.set_main_option("script_location", str(alembic_dir))
        self.alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    def create_tables(self):
        """创建所有表（同步方式）"""
        Base.metadata.create_all(bind=self.engine)
        print("所有表已创建")
    
    def drop_tables(self):
        """删除所有表"""
        Base.metadata.drop_all(bind=self.engine)
        print("所有表已删除")
    
    def alembic_upgrade(self, revision="head"):
        """执行Alembic升级迁移"""
        try:
            command.upgrade(self.alembic_cfg, revision)
            print(f"数据库已迁移到 {revision} 版本")
        except Exception as e:
            print(f"迁移升级失败: {e}")
            raise
    
    def alembic_downgrade(self, revision):
        """执行Alembic降级迁移"""
        try:
            command.downgrade(self.alembic_cfg, revision)
            print(f"数据库已降级到 {revision} 版本")
        except Exception as e:
            print(f"迁移降级失败: {e}")
            raise
    
    def alembic_current(self):
        """查看当前数据库版本"""
        try:
            command.current(self.alembic_cfg)
        except Exception as e:
            print(f"查看当前版本失败: {e}")
            raise
    
    def alembic_history(self):
        """查看迁移历史"""
        try:
            command.history(self.alembic_cfg)
        except Exception as e:
            print(f"查看历史失败: {e}")
            raise
    
    def alembic_stamp(self, revision):
        """标记数据库版本（不实际执行迁移）"""
        try:
            command.stamp(self.alembic_cfg, revision)
            print(f"数据库版本已标记为 {revision}")
        except Exception as e:
            print(f"版本标记失败: {e}")
            raise
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()


# 便捷函数
def get_database_migration_manager(database_url: str = None) -> DatabaseMigrationManager:
    """获取数据库迁移管理器实例"""
    if database_url is None:
        # 从环境变量或默认配置获取数据库URL
        database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    return DatabaseMigrationManager(database_url)


# 示例使用
if __name__ == "__main__":
    # 创建迁移管理器实例
    db_manager = get_database_migration_manager("sqlite:///./test_industrial.db")
    
    # 执行数据库迁移
    print("开始数据库迁移...")
    db_manager.alembic_upgrade()
    print("数据库迁移完成!")