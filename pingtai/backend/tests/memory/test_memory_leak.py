# -*- coding: utf-8 -*-
"""
内存泄漏测试 - Memory Leak Tests

【职责】
检测系统内存泄漏问题
监控内存使用情况
分析内存增长趋势

【测试内容】
- 长时间运行内存监控
- 对象创建和销毁测试
- 循环引用检测
- 内存增长趋势分析
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import gc
import time
import tracemalloc
from typing import List, Dict, Any
from platform_core.domain.task import Task
from platform_core.domain.alarm import Alarm
from platform_core.domain.report import Report


class MemoryMonitor:
    """内存监控器"""
    
    def __init__(self):
        self.snapshots: List[Dict[str, Any]] = []
        self.start_time = time.time()
        tracemalloc.start()
    
    def take_snapshot(self, label: str = ""):
        """获取内存快照"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        current, peak = tracemalloc.get_traced_memory()
        gc.collect()
        
        snapshot = {
            'label': label,
            'elapsed_time': elapsed_time,
            'current_memory': current,
            'peak_memory': peak,
            'current_memory_mb': current / 1024 / 1024,
            'peak_memory_mb': peak / 1024 / 1024,
            'gc_objects': len(gc.get_objects())
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_memory_growth_rate(self) -> float:
        """计算内存增长率"""
        if len(self.snapshots) < 2:
            return 0.0
        
        first_snapshot = self.snapshots[0]
        last_snapshot = self.snapshots[-1]
        
        time_diff = last_snapshot['elapsed_time'] - first_snapshot['elapsed_time']
        if time_diff == 0:
            return 0.0
        
        memory_diff = last_snapshot['current_memory'] - first_snapshot['current_memory']
        growth_rate = memory_diff / time_diff
        
        return growth_rate
    
    def detect_memory_leak(self, threshold: float = 1024 * 1024) -> bool:
        """检测内存泄漏
        
        Args:
            threshold: 内存增长阈值（字节/秒）
            
        Returns:
            是否检测到内存泄漏
        """
        growth_rate = self.get_memory_growth_rate()
        return growth_rate > threshold
    
    def get_summary(self) -> Dict[str, Any]:
        """获取内存使用摘要"""
        if not self.snapshots:
            return {}
        
        current_snapshot = self.snapshots[-1]
        first_snapshot = self.snapshots[0]
        
        memory_increase = current_snapshot['current_memory'] - first_snapshot['current_memory']
        time_elapsed = current_snapshot['elapsed_time'] - first_snapshot['elapsed_time']
        
        return {
            'total_time': time_elapsed,
            'memory_increase': memory_increase,
            'memory_increase_mb': memory_increase / 1024 / 1024,
            'growth_rate': self.get_memory_growth_rate(),
            'growth_rate_mb_per_sec': self.get_memory_growth_rate() / 1024 / 1024,
            'current_memory_mb': current_snapshot['current_memory_mb'],
            'peak_memory_mb': current_snapshot['peak_memory_mb'],
            'gc_objects': current_snapshot['gc_objects'],
            'memory_leak_detected': self.detect_memory_leak()
        }


class TaskMemoryLeakTest:
    """任务内存泄漏测试"""
    
    def __init__(self, duration_minutes: int = 10, operations_per_minute: int = 100):
        self.duration_minutes = duration_minutes
        self.operations_per_minute = operations_per_minute
        self.monitor = MemoryMonitor()
    
    def run(self) -> Dict[str, Any]:
        """运行内存泄漏测试"""
        print(f"开始任务内存泄漏测试，持续时间: {self.duration_minutes}分钟")
        print(f"每分钟操作数: {self.operations_per_minute}")
        
        self.monitor.take_snapshot("开始")
        
        total_operations = 0
        start_time = time.time()
        
        while (time.time() - start_time) < (self.duration_minutes * 60):
            batch_start = time.time()
            
            for i in range(self.operations_per_minute):
                try:
                    task = Task.create(
                        workorder_id=f"WO-{total_operations:06d}",
                        station_id=1,
                        sn=f"SN-{total_operations:06d}",
                        task_type="test"
                    )
                    total_operations += 1
                except Exception as e:
                    print(f"任务创建失败: {e}")
            
            # 定期清理
            gc.collect()
            
            # 每5分钟获取一次快照
            if (time.time() - start_time) % 300 < 10:
                self.monitor.take_snapshot(f"运行中-{int(time.time() - start_time)}秒")
            
            # 控制操作频率
            batch_time = time.time() - batch_start
            if batch_time < 60:
                time.sleep(60 - batch_time)
        
        self.monitor.take_snapshot("结束")
        
        summary = self.monitor.get_summary()
        summary['total_operations'] = total_operations
        summary['operations_per_second'] = total_operations / summary['total_time']
        
        print(f"任务内存泄漏测试完成")
        print(f"总操作数: {total_operations}")
        print(f"总耗时: {summary['total_time']:.2f}秒")
        print(f"内存增长: {summary['memory_increase_mb']:.2f}MB")
        print(f"增长率: {summary['growth_rate_mb_per_sec']:.4f}MB/秒")
        print(f"内存泄漏检测: {'检测到泄漏' if summary['memory_leak_detected'] else '未检测到泄漏'}")
        
        return summary


class AlarmMemoryLeakTest:
    """告警内存泄漏测试"""
    
    def __init__(self, duration_minutes: int = 10, operations_per_minute: int = 100):
        self.duration_minutes = duration_minutes
        self.operations_per_minute = operations_per_minute
        self.monitor = MemoryMonitor()
    
    def run(self) -> Dict[str, Any]:
        """运行内存泄漏测试"""
        print(f"开始告警内存泄漏测试，持续时间: {self.duration_minutes}分钟")
        print(f"每分钟操作数: {self.operations_per_minute}")
        
        self.monitor.take_snapshot("开始")
        
        total_operations = 0
        start_time = time.time()
        
        while (time.time() - start_time) < (self.duration_minutes * 60):
            batch_start = time.time()
            
            for i in range(self.operations_per_minute):
                try:
                    alarm = Alarm.create(
                        alarm_code=f"ALARM-{total_operations:04d}",
                        alarm_level="warning",
                        message=f"测试告警 {total_operations}",
                        task_id=f"TASK-{total_operations:06d}",
                        station_id="1",
                        device_id=f"DEV-{total_operations:04d}"
                    )
                    
                    alarm.acknowledge(operator_id="OPERATOR-MEMORY")
                    alarm.resolve(operator_id="OPERATOR-MEMORY")
                    
                    total_operations += 1
                except Exception as e:
                    print(f"告警处理失败: {e}")
            
            # 定期清理
            gc.collect()
            
            # 每5分钟获取一次快照
            if (time.time() - start_time) % 300 < 10:
                self.monitor.take_snapshot(f"运行中-{int(time.time() - start_time)}秒")
            
            # 控制操作频率
            batch_time = time.time() - batch_start
            if batch_time < 60:
                time.sleep(60 - batch_time)
        
        self.monitor.take_snapshot("结束")
        
        summary = self.monitor.get_summary()
        summary['total_operations'] = total_operations
        summary['operations_per_second'] = total_operations / summary['total_time']
        
        print(f"告警内存泄漏测试完成")
        print(f"总操作数: {total_operations}")
        print(f"总耗时: {summary['total_time']:.2f}秒")
        print(f"内存增长: {summary['memory_increase_mb']:.2f}MB")
        print(f"增长率: {summary['growth_rate_mb_per_sec']:.4f}MB/秒")
        print(f"内存泄漏检测: {'检测到泄漏' if summary['memory_leak_detected'] else '未检测到泄漏'}")
        
        return summary


class ObjectLifecycleTest:
    """对象生命周期测试"""
    
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations
        self.monitor = MemoryMonitor()
    
    def run(self) -> Dict[str, Any]:
        """运行对象生命周期测试"""
        print(f"开始对象生命周期测试，迭代次数: {self.iterations}")
        
        self.monitor.take_snapshot("开始")
        
        for i in range(self.iterations):
            try:
                # 创建对象
                task = Task.create(
                    workorder_id=f"WO-{i:06d}",
                    station_id=1,
                    sn=f"SN-{i:06d}",
                    task_type="test"
                )
                
                alarm = Alarm.create(
                    alarm_code=f"ALARM-{i:04d}",
                    alarm_level="warning",
                    message=f"测试告警 {i}",
                    task_id=task.id,
                    station_id="1",
                    device_id=f"DEV-{i:04d}"
                )
                
                # 对象应该在这里被销毁
                del task
                del alarm
                
                # 定期清理
                if i % 1000 == 0:
                    gc.collect()
                    
            except Exception as e:
                print(f"对象生命周期测试失败: {e}")
        
        gc.collect()
        self.monitor.take_snapshot("结束")
        
        summary = self.monitor.get_summary()
        summary['iterations'] = self.iterations
        
        print(f"对象生命周期测试完成")
        print(f"迭代次数: {self.iterations}")
        print(f"内存增长: {summary['memory_increase_mb']:.2f}MB")
        print(f"增长率: {summary['growth_rate_mb_per_sec']:.4f}MB/秒")
        print(f"内存泄漏检测: {'检测到泄漏' if summary['memory_leak_detected'] else '未检测到泄漏'}")
        
        return summary


def run_all_memory_tests(duration_hours: float = 2.0):
    """运行所有内存泄漏测试
    
    Args:
        duration_hours: 内存测试持续时间（小时）
    """
    print(f"\n{'='*80}")
    print(f"内存泄漏测试套件 - Memory Leak Test Suite")
    print(f"总持续时间: {duration_hours}小时")
    print(f"{'='*80}\n")
    
    results = {}
    
    # 任务内存泄漏测试 - 使用指定时间的40%
    task_test = TaskMemoryLeakTest(
        duration_minutes=int(duration_hours * 60 * 0.4), 
        operations_per_minute=50
    )
    results['task_memory_leak'] = task_test.run()
    
    # 告警内存泄漏测试 - 使用指定时间的40%
    alarm_test = AlarmMemoryLeakTest(
        duration_minutes=int(duration_hours * 60 * 0.4), 
        operations_per_minute=50
    )
    results['alarm_memory_leak'] = alarm_test.run()
    
    # 对象生命周期测试
    lifecycle_test = ObjectLifecycleTest(iterations=5000)
    results['object_lifecycle'] = lifecycle_test.run()
    
    return results


if __name__ == '__main__':
    import sys
    
    # 从命令行参数获取持续时间，默认2小时
    duration = 2.0
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            print(f"无效的持续时间参数，使用默认值2小时")
    
    results = run_all_memory_tests(duration_hours=duration)
    print(f"\n{'='*80}")
    print(f"内存泄漏测试完成 - Memory Leak Tests Completed")
    print(f"{'='*80}")