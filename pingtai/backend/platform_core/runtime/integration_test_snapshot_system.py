"""
快照恢复体系综合测试
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from encoder_test.runtime.snapshot.snapshot_manager import SnapshotManager, RuntimeSnapshot
from encoder_test.runtime.snapshot.recovery_manager import RecoveryManager
from encoder_test.runtime.snapshot.snapshot_policy import SnapshotPolicy
from encoder_test.runtime.actor.mailbox import PriorityMailbox, MessagePriority, ActorMessage
from encoder_test.runtime.health.health_monitor import HealthMonitor
from encoder_test.runtime.health.heartbeat_monitor import HeartbeatMonitor
from encoder_test.domain.common.idempotent import IdempotencyManager, IdempotentCommand, get_idempotency_manager


async def test_snapshot_system():
    """测试快照系统"""
    print("=" * 60)
    print("测试快照系统")
    print("=" * 60)
    
    # 创建快照管理器
    snapshot_manager = SnapshotManager("./test_snapshots")
    
    # 模拟运行时状态
    runtime_state = {
        'station_states': {'station_1': 'RUNNING', 'station_2': 'IDLE'},
        'actor_states': {'actor_1': {'status': 'ACTIVE', 'queue_size': 5}},
        'task_states': {'task_1': {'status': 'RUNNING', 'progress': 0.5}},
        'device_states': {'device_1': {'status': 'ONLINE', 'connection': 'TCP'}},
    }
    
    # 创建快照
    print("1. 创建快照...")
    snapshot_id = await snapshot_manager.create_snapshot(runtime_state)
    print(f"   快照创建成功: {snapshot_id}")
    
    # 加载快照
    print("2. 加载最新快照...")
    loaded_snapshot = await snapshot_manager.load_latest_snapshot()
    if loaded_snapshot:
        print(f"   加载快照: {loaded_snapshot.snapshot_id}")
        print(f"   创建时间: {loaded_snapshot.created_at}")
    
    # 清理旧快照
    print("3. 清理旧快照...")
    await snapshot_manager.cleanup_old_snapshots(keep_last_n=3)
    print("   旧快照清理完成")
    
    return snapshot_manager


async def test_recovery_system(snapshot_manager):
    """测试恢复系统"""
    print("\n" + "=" * 60)
    print("测试恢复系统")
    print("=" * 60)
    
    # 创建恢复管理器
    recovery_manager = RecoveryManager(snapshot_manager)
    
    print("1. 尝试恢复系统...")
    success = await recovery_manager.attempt_recovery()
    print(f"   恢复结果: {'成功' if success else '失败'}")
    
    print("2. 测试业务一致性校验...")
    # 创建一个模拟快照用于测试
    test_snapshot = RuntimeSnapshot(
        snapshot_id="test_snapshot",
        created_at=datetime.now(),
        station_states={'station_1': 'RUNNING'},
        actor_states={'actor_1': {'status': 'RUNNING'}},
        task_states={'task_1': {'status': 'RUNNING', 'device_id': 'device_1'}},
        device_states={'device_1': {'status': 'OFFLINE'}},  # 设备离线但任务运行
        runtime_version="1.0.0"
    )
    
    await recovery_manager._validate_business_consistency(test_snapshot)
    print("   业务一致性校验完成")


async def test_actor_mailbox():
    """测试Actor邮箱系统"""
    print("\n" + "=" * 60)
    print("测试Actor邮箱系统")
    print("=" * 60)
    
    mailbox = PriorityMailbox(max_size=10)
    
    # 创建不同类型的消息
    critical_msg = ActorMessage(
        message_id="crit_1",
        priority=MessagePriority.CRITICAL,
        content="Emergency Stop",
        timestamp=1234567890.0
    )
    
    normal_msg = ActorMessage(
        message_id="norm_1", 
        priority=MessagePriority.NORMAL,
        content="Status Update",
        timestamp=1234567891.0
    )
    
    transient_msg = ActorMessage(
        message_id="trans_1",
        priority=MessagePriority.TRANSIENT, 
        content="Heartbeat",
        timestamp=1234567892.0
    )
    
    print("1. 添加消息到邮箱...")
    mailbox.put(critical_msg)
    mailbox.put(normal_msg)
    mailbox.put(transient_msg)
    
    print("2. 检查邮箱状态...")
    stats = mailbox.get_stats()
    print(f"   邮箱统计: {stats}")
    
    print("3. 获取消息...")
    msg = mailbox.get()
    if msg:
        print(f"   获取消息: {msg.message_id}, 优先级: {msg.priority}")


async def test_health_monitoring():
    """测试健康监控系统"""
    print("\n" + "=" * 60)
    print("测试健康监控系统")
    print("=" * 60)
    
    health_monitor = HealthMonitor()
    
    print("1. 启动健康监控...")
    await health_monitor.start_monitoring()
    
    print("2. 获取当前健康状态...")
    current_health = await health_monitor.get_current_health()
    print(f"   内存使用: {current_health.memory_usage_mb:.2f}MB")
    print(f"   CPU使用率: {current_health.cpu_percent}%")
    
    print("3. 获取健康趋势...")
    trend = await health_monitor.get_health_trend(minutes=1)
    print(f"   健康记录数: {len(trend)}")
    
    # 停止监控
    health_monitor.stop_monitoring()
    print("   健康监控已停止")


async def test_idempotency():
    """测试幂等性系统"""
    print("\n" + "=" * 60)
    print("测试幂等性系统")
    print("=" * 60)
    
    idempotency_mgr = get_idempotency_manager()
    
    # 创建相同的命令多次
    cmd1 = IdempotentCommand(content={"action": "start_task", "task_id": "task_1"})
    cmd2 = IdempotentCommand(content={"action": "start_task", "task_id": "task_1"})  # 相同内容
    
    async def dummy_handler(cmd):
        print(f"   执行命令: {cmd.command_id}")
        return "executed"
    
    print("1. 执行第一次命令...")
    result1 = await idempotency_mgr.execute_if_not_processed(cmd1, dummy_handler)
    print(f"   结果: {result1}")
    
    print("2. 执行第二次相同命令...")
    result2 = await idempotency_mgr.execute_if_not_processed(cmd2, dummy_handler)
    print(f"   结果: {result2} (应该为None，因为已处理过)")
    
    print("3. 检查幂等性管理器状态...")
    stats = idempotency_mgr.get_stats()
    print(f"   已处理命令数: {stats['processed_count']}")


async def main():
    """主测试函数"""
    print("工业平台快照恢复体系综合测试")
    print("=" * 60)
    
    # 依次测试各个子系统
    snapshot_manager = await test_snapshot_system()
    await test_recovery_system(snapshot_manager)
    await test_actor_mailbox()
    await test_health_monitoring()
    await test_idempotency()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())