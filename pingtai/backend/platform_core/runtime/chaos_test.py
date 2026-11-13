"""
工业自动化测试平台 - 混沌测试脚本
用于长时间运行和内存泄漏检测
"""
import asyncio
import threading
import time
import gc
import psutil
import os
from datetime import datetime
import logging
from encoder_test.runtime.event_bus import get_event_bus, publish_event
from encoder_test.runtime.events import (
    TaskStarted, TaskCompleted, TaskFailed,
    AlarmTriggered, AlarmResolved,
    DeviceConnected, DeviceDisconnected,
    WorkOrderStarted, WorkOrderCompleted
)
from encoder_test.runtime.event_manager import start_runtime_event_manager, stop_runtime_event_manager
from encoder_test.runtime.persistence_worker import initialize_persistence_worker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from encoder_test.storage.models import Base, TaskModel, AlarmModel, DeviceModel, WorkOrderModel
from encoder_test.application.workorder.repository_impl import WorkOrderRepository


class ChaosTester:
    """混沌测试器"""
    
    def __init__(self, duration_hours=14):
        self.duration_seconds = duration_hours * 3600
        self.start_time = None
        self.process = psutil.Process(os.getpid())
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """设置日志"""
        logger = logging.getLogger('ChaosTester')
        logger.setLevel(logging.INFO)
        
        # 文件处理器
        fh = logging.FileHandler(f'chaos_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        fh.setLevel(logging.INFO)
        
        # 控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def monitor_resources(self):
        """监控系统资源"""
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent()
        
        # 获取垃圾回收信息
        gc_counts = gc.get_count()
        
        self.logger.info(f"内存使用: RSS={memory_info.rss / 1024 / 1024:.2f}MB, "
                        f"VMS={memory_info.vms / 1024 / 1024:.2f}MB | "
                        f"CPU使用率: {cpu_percent}% | "
                        f"垃圾回收: {gc_counts}")
        
        return {
            'memory_rss_mb': memory_info.rss / 1024 / 1024,
            'memory_vms_mb': memory_info.vms / 1024 / 1024,
            'cpu_percent': cpu_percent,
            'gc_counts': gc_counts
        }
    
    async def simulate_events(self):
        """模拟各种事件"""
        event_types = [
            ("TaskStarted", lambda i: TaskStarted(
                event_id=f"TASK_START_{i}",
                timestamp=datetime.utcnow(),
                source="ChaosTest",
                payload={"test_data": f"data_{i}"},
                task_id=f"CHAOS_TASK_{i % 100}",  # 循环使用100个任务ID
                actor_id=f"ACTOR_{i % 10}"
            )),
            ("TaskCompleted", lambda i: TaskCompleted(
                event_id=f"TASK_COMP_{i}",
                timestamp=datetime.utcnow(),
                source="ChaosTest",
                payload={"test_data": f"data_{i}"},
                task_id=f"CHAOS_TASK_{i % 100}",
                result="PASS" if i % 3 != 0 else "FAIL",
                duration_ms=100 + (i % 500)
            )),
            ("AlarmTriggered", lambda i: AlarmTriggered(
                event_id=f"ALARM_TRIG_{i}",
                timestamp=datetime.utcnow(),
                source="ChaosTest",
                payload={"test_data": f"data_{i}"},
                alarm_id=f"CHAOS_ALARM_{i % 50}",
                alarm_code="TEST_ERROR" if i % 2 == 0 else "SYSTEM_WARNING",
                alarm_level="ERROR" if i % 3 == 0 else "WARNING",
                message=f"Chaos test alarm {i}"
            )),
            ("DeviceConnected", lambda i: DeviceConnected(
                event_id=f"DEV_CONN_{i}",
                timestamp=datetime.utcnow(),
                source="ChaosTest",
                payload={"test_data": f"data_{i}"},
                device_id=f"CHAOS_DEV_{i % 20}",
                connection_info={"ip": f"192.168.1.{i % 254}", "port": 8080 + (i % 100)}
            )),
            ("DeviceDisconnected", lambda i: DeviceDisconnected(
                event_id=f"DEV_DISC_{i}",
                timestamp=datetime.utcnow(),
                source="ChaosTest",
                payload={"test_data": f"data_{i}"},
                device_id=f"CHAOS_DEV_{i % 20}",
                reason="Chaos test disconnection"
            ))
        ]
        
        counter = 0
        while self.running:
            # 随机选择事件类型
            import random
            event_type, event_creator = random.choice(event_types)
            
            try:
                event = event_creator(counter)
                await publish_event(event)
                
                if counter % 100 == 0:
                    self.logger.info(f"已发布 {counter} 个事件")
                
                counter += 1
                
                # 随机延迟，模拟真实场景
                delay = min(0.1, random.uniform(0.01, 0.1))
                await asyncio.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"发布事件时出错: {e}")
    
    async def run_memory_monitoring(self):
        """运行内存监控"""
        initial_memory = None
        peak_memory = 0
        measurement_count = 0
        total_memory = 0
        
        while self.running:
            resource_info = self.monitor_resources()
            current_memory = resource_info['memory_rss_mb']
            
            if initial_memory is None:
                initial_memory = current_memory
            peak_memory = max(peak_memory, current_memory)
            total_memory += current_memory
            measurement_count += 1
            
            # 每分钟汇总一次
            if measurement_count % 600 == 0:  # 假设每秒监测一次
                avg_memory = total_memory / measurement_count
                self.logger.info(f"内存统计 - 初始: {initial_memory:.2f}MB, "
                                f"平均: {avg_memory:.2f}MB, "
                                f"峰值: {peak_memory:.2f}MB, "
                                f"增长: {current_memory - initial_memory:.2f}MB")
            
            # 每10秒执行一次垃圾回收
            if measurement_count % 10 == 0:
                collected = gc.collect()
                self.logger.debug(f"垃圾回收: {collected} 个对象被回收")
            
            await asyncio.sleep(1)  # 每秒监测一次
    
    async def run_test(self):
        """运行混沌测试"""
        self.logger.info(f"开始混沌测试，持续时间: {self.duration_seconds / 3600:.1f} 小时")
        self.start_time = time.time()
        self.running = True
        
        try:
            # 启动运行时事件管理器
            self.logger.info("启动运行时事件管理器...")
            start_runtime_event_manager()
            
            # 创建临时数据库用于测试
            engine = create_engine("sqlite:///chaos_test.db", echo=False)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            
            # 初始化持久化工作器
            workorder_repo = WorkOrderRepository(Session)
            initialize_persistence_worker(Session, workorder_repo)
            
            # 启动事件模拟和内存监控任务
            tasks = [
                asyncio.create_task(self.simulate_events()),
                asyncio.create_task(self.run_memory_monitoring())
            ]
            
            # 等待测试完成
            start_time = time.time()
            while time.time() - start_time < self.duration_seconds and self.running:
                await asyncio.sleep(1)
            
            self.running = False
            
            # 等待所有任务完成
            for task in tasks:
                task.cancel()
            
            # 执行最终的资源检查
            final_resources = self.monitor_resources()
            self.logger.info("混沌测试完成")
            self.logger.info(f"最终资源使用: 内存RSS={final_resources['memory_rss_mb']:.2f}MB")
            
        except Exception as e:
            self.logger.error(f"混沌测试期间发生错误: {e}", exc_info=True)
        finally:
            # 停止运行时事件管理器
            try:
                stop_runtime_event_manager()
                self.logger.info("运行时事件管理器已停止")
            except:
                pass


def main():
    """主函数"""
    print("工业自动化测试平台 - 混沌测试启动器")
    print("=" * 50)
    print("即将开始14小时混沌测试...")
    print("测试内容:")
    print("- 持续发布各种类型的事件")
    print("- 实时监控内存使用情况")
    print("- 检测潜在的内存泄漏")
    print("- 记录系统资源使用统计")
    print("=" * 50)
    
    tester = ChaosTester(duration_hours=14)
    
    try:
        asyncio.run(tester.run_test())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    
    print("混沌测试结束，请检查 chaos_test_*.log 文件获取详细结果")


if __name__ == "__main__":
    main()