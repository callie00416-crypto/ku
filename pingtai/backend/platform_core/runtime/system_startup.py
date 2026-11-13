"""
工业平台运行时系统启动器
实现完整的快照恢复和健康监控体系
"""
import asyncio
import logging
import signal
import sys
import os
from datetime import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class IndustrialRuntimeSystem:
    """工业运行时系统"""
    
    def __init__(self):
        self.snapshot_manager = None
        self.recovery_manager = None
        self.health_monitor = None
        self.heartbeat_monitor = None
        self.watchdog = None
        self.deadlock_detector = None
        self.idempotency_manager = None
        self.is_running = False
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，正在关闭系统...")
            asyncio.create_task(self.shutdown())
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def initialize(self):
        """初始化系统组件"""
        logger.info("正在初始化工业运行时系统...")
        
        # 1. 初始化幂等性管理器（优先级最高）
        from encoder_test.domain.common.idempotent import get_idempotency_manager
        self.idempotency_manager = get_idempotency_manager()
        logger.info("✓ 幂等性管理器初始化完成")
        
        # 2. 初始化快照系统
        from encoder_test.runtime.snapshot.snapshot_manager import SnapshotManager
        from encoder_test.runtime.snapshot.recovery_manager import RecoveryManager
        self.snapshot_manager = SnapshotManager("./snapshots")
        self.recovery_manager = RecoveryManager(self.snapshot_manager)
        logger.info("✓ 快照系统初始化完成")
        
        # 3. 初始化健康监控系统
        from encoder_test.runtime.health.health_monitor import HealthMonitor
        from encoder_test.runtime.health.heartbeat_monitor import HeartbeatMonitor
        from encoder_test.runtime.health.watchdog import Watchdog
        from encoder_test.runtime.health.deadlock_detector import DeadlockDetector
        self.health_monitor = HealthMonitor()
        self.heartbeat_monitor = HeartbeatMonitor()
        self.watchdog = Watchdog(timeout=300)  # 5分钟超时
        self.deadlock_detector = DeadlockDetector()
        logger.info("✓ 健康监控系统初始化完成")
        
        # 4. 注册系统组件到心跳监控
        self.heartbeat_monitor.register_component("snapshot_manager")
        self.heartbeat_monitor.register_component("recovery_manager")
        self.heartbeat_monitor.register_component("health_monitor")
        
        logger.info("系统组件初始化完成")
        
    async def start_recovery_process(self):
        """启动恢复过程"""
        logger.info("开始系统恢复过程...")
        
        # 尝试从快照恢复
        recovery_success = await self.recovery_manager.attempt_recovery()
        if recovery_success:
            logger.info("✓ 系统恢复成功")
        else:
            logger.warning("⚠ 系统恢复过程中出现问题，使用默认状态启动")
            
        # 启动监控系统
        await self.health_monitor.start_monitoring()
        await self.heartbeat_monitor.start_monitoring()
        await self.watchdog.start()
        await self.deadlock_detector.start_detection()
        
        logger.info("✓ 监控系统已启动")
        
    async def main_loop(self):
        """主循环"""
        logger.info("工业运行时系统已启动")
        self.is_running = True
        
        while self.is_running:
            try:
                # 更新心跳
                self.heartbeat_monitor.heartbeat("runtime_system")
                
                # 喂狗
                self.watchdog.kick()
                
                # 模拟一些运行时活动
                await asyncio.sleep(10)  # 实际系统中这里会处理业务逻辑
                
            except asyncio.CancelledError:
                logger.info("主循环被取消")
                break
            except Exception as e:
                logger.error(f"主循环错误: {e}", exc_info=True)
                # 记录错误但不停止系统
                
    async def shutdown(self):
        """关闭系统"""
        if not self.is_running:
            return
            
        logger.info("正在关闭工业运行时系统...")
        self.is_running = False
        
        # 停止监控系统
        if self.health_monitor:
            self.health_monitor.stop_monitoring()
        if self.heartbeat_monitor:
            self.heartbeat_monitor.stop_monitoring()
        if self.watchdog:
            await self.watchdog.stop()
        if self.deadlock_detector:
            await self.deadlock_detector.stop_detection()
            
        logger.info("工业运行时系统已关闭")
        
    async def run(self):
        """运行系统"""
        try:
            # 初始化系统
            await self.initialize()
            
            # 执行恢复过程
            await self.start_recovery_process()
            
            # 运行主循环
            await self.main_loop()
            
        except KeyboardInterrupt:
            logger.info("收到键盘中断信号")
        except Exception as e:
            logger.error(f"系统运行错误: {e}", exc_info=True)
        finally:
            await self.shutdown()


async def create_system_snapshot(runtime_system):
    """创建系统快照的辅助函数"""
    if runtime_system.snapshot_manager:
        # 获取当前运行时状态（简化版）
        runtime_state = {
            'station_states': {},
            'actor_states': {},
            'task_states': {},
            'device_states': {},
            'timestamp': datetime.now().isoformat()
        }
        
        snapshot_id = await runtime_system.snapshot_manager.create_snapshot(runtime_state)
        logger.info(f"系统快照创建: {snapshot_id}")
        return snapshot_id
    return None


def main():
    """主函数"""
    logger.info("启动工业自动化测试平台运行时系统")
    
    # 创建并运行系统
    runtime_system = IndustrialRuntimeSystem()
    
    try:
        asyncio.run(runtime_system.run())
    except KeyboardInterrupt:
        logger.info("系统被用户中断")
    except Exception as e:
        logger.error(f"系统启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()