# -*- coding: utf-8 -*-
"""
稳定性测试 - Stability Tests

【职责】
测试系统长时间运行的稳定性
验证系统在负载下的表现
检测系统降级和故障恢复

【测试内容】
- 长时间运行测试
- 负载测试
- 故障恢复测试
- 资源耗尽测试
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径（必须在导入platform之前）
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 确保使用项目的platform包，而不是Python内置的platform模块
if 'platform_core' in sys.modules:
    del sys.modules['platform_core']

import time
import threading
import random
from typing import List, Dict, Any
from platform_core.domain.task import Task
from platform_core.domain.alarm import Alarm
from platform_core.domain.report import Report


class StabilityMonitor:
    """稳定性监控器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.errors: List[Dict[str, Any]] = []
        self.success_count: int = 0
        self.failure_count: int = 0
        self.response_times: List[float] = []
    
    def record_success(self, response_time: float = 0.0):
        """记录成功"""
        self.success_count += 1
        if response_time > 0:
            self.response_times.append(response_time)
    
    def record_failure(self, error: Exception, context: str = ""):
        """记录失败"""
        self.failure_count += 1
        self.errors.append({
            'timestamp': time.time(),
            'error': str(error),
            'context': context
        })
    
    def get_stability_metrics(self) -> Dict[str, Any]:
        """获取稳定性指标"""
        elapsed_time = time.time() - self.start_time
        total_operations = self.success_count + self.failure_count
        
        if total_operations == 0:
            return {
                'elapsed_time': elapsed_time,
                'success_rate': 0.0,
                'error_rate': 0.0,
                'operations_per_second': 0.0,
                'avg_response_time': 0.0,
                'error_count': 0
            }
        
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
        
        return {
            'elapsed_time': elapsed_time,
            'success_rate': self.success_count / total_operations,
            'error_rate': self.failure_count / total_operations,
            'operations_per_second': total_operations / elapsed_time,
            'avg_response_time': avg_response_time,
            'error_count': len(self.errors)
        }


class LongRunningStabilityTest:
    """长时间运行稳定性测试"""
    
    def __init__(self, duration_hours: float = 1.0, operations_per_minute: int = 60):
        self.duration_hours = duration_hours
        self.operations_per_minute = operations_per_minute
        self.monitor = StabilityMonitor()
        self.running = True
    
    def worker_thread(self, thread_id: int):
        """工作线程"""
        operation_count = 0
        
        while self.running:
            try:
                start_time = time.time()
                
                # 随机选择操作类型
                operation_type = random.choice(['task', 'alarm', 'report'])
                
                if operation_type == 'task':
                    task = Task.create(
                        workorder_id=f"WO-T{thread_id}-{operation_count:06d}",
                        station_id=thread_id % 10 + 1,
                        sn=f"SN-T{thread_id}-{operation_count:06d}",
                        task_type="test"
                    )
                    task.start(actor_id=f"ACTOR-T{thread_id}")
                    task.complete()
                
                elif operation_type == 'alarm':
                    alarm = Alarm.create(
                        alarm_code=f"ALARM-T{thread_id}-{operation_count:04d}",
                        alarm_level=random.choice(['info', 'warning', 'error']),
                        message=f"测试告警 {operation_count}",
                        task_id=f"TASK-{operation_count:06d}",
                        station_id=str(thread_id % 10 + 1),
                        device_id=f"DEV-{operation_count:04d}"
                    )
                    alarm.acknowledge(operator_id=f"OPERATOR-T{thread_id}")
                    alarm.resolve(operator_id=f"OPERATOR-T{thread_id}")
                
                elif operation_type == 'report':
                    task = Task.create(
                        workorder_id=f"WO-T{thread_id}-{operation_count:06d}",
                        station_id=thread_id % 10 + 1,
                        sn=f"SN-T{thread_id}-{operation_count:06d}",
                        task_type="test"
                    )
                    
                    report = Report.create(
                        task_id=task.id,
                        workorder_id=f"WO-T{thread_id}-{operation_count:06d}",
                        sn=f"SN-T{thread_id}-{operation_count:06d}"
                    )
                
                response_time = time.time() - start_time
                self.monitor.record_success(response_time)
                operation_count += 1
                
                # 控制操作频率
                time.sleep(60 / self.operations_per_minute)
                
            except Exception as e:
                self.monitor.record_failure(e, f"Thread-{thread_id}")
                print(f"线程{thread_id}操作失败: {e}")
                time.sleep(1)
    
    def run(self) -> Dict[str, Any]:
        """运行长时间稳定性测试"""
        print(f"开始长时间运行稳定性测试")
        print(f"持续时间: {self.duration_hours}小时")
        print(f"每分钟操作数: {self.operations_per_minute}")
        
        # 创建工作线程
        num_threads = 4
        threads = []
        
        for i in range(num_threads):
            thread = threading.Thread(target=self.worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 监控线程
        def monitor_thread():
            while self.running:
                time.sleep(300)  # 每5分钟输出一次状态
                metrics = self.monitor.get_stability_metrics()
                print(f"运行状态 - 成功率: {metrics['success_rate']*100:.2f}%, "
                      f"错误率: {metrics['error_rate']*100:.2f}%, "
                      f"操作/秒: {metrics['operations_per_second']:.2f}")
        
        monitor = threading.Thread(target=monitor_thread)
        monitor.start()
        
        # 等待测试完成
        time.sleep(self.duration_hours * 3600)
        self.running = False
        
        # 等待所有线程结束
        for thread in threads:
            thread.join()
        
        monitor.join()
        
        results = self.monitor.get_stability_metrics()
        results['duration_hours'] = self.duration_hours
        results['num_threads'] = num_threads
        results['operations_per_minute'] = self.operations_per_minute
        
        print(f"长时间运行稳定性测试完成")
        print(f"总耗时: {results['elapsed_time']:.2f}秒")
        print(f"成功率: {results['success_rate']*100:.2f}%")
        print(f"错误率: {results['error_rate']*100:.2f}%")
        print(f"操作/秒: {results['operations_per_second']:.2f}")
        print(f"平均响应时间: {results['avg_response_time']*1000:.2f}毫秒")
        print(f"错误总数: {results['error_count']}")
        
        return results


class LoadStabilityTest:
    """负载稳定性测试"""
    
    def __init__(self, duration_minutes: int = 30, max_concurrent_operations: int = 100):
        self.duration_minutes = duration_minutes
        self.max_concurrent_operations = max_concurrent_operations
        self.monitor = StabilityMonitor()
    
    def run(self) -> Dict[str, Any]:
        """运行负载稳定性测试"""
        print(f"开始负载稳定性测试")
        print(f"持续时间: {self.duration_minutes}分钟")
        print(f"最大并发操作数: {self.max_concurrent_operations}")
        
        start_time = time.time()
        operation_count = 0
        
        while (time.time() - start_time) < (self.duration_minutes * 60):
            try:
                iteration_start = time.time()
                
                # 创建多个并发操作
                operations = []
                for i in range(min(self.max_concurrent_operations, 50)):
                    try:
                        task = Task.create(
                            workorder_id=f"WO-{operation_count:06d}",
                            station_id=random.randint(1, 10),
                            sn=f"SN-{operation_count:06d}",
                            task_type="test"
                        )
                        operations.append(task)
                        operation_count += 1
                    except Exception as e:
                        self.monitor.record_failure(e, "task_creation")
                
                response_time = time.time() - iteration_start
                self.monitor.record_success(response_time)
                
                # 控制负载
                time.sleep(1)
                
            except Exception as e:
                self.monitor.record_failure(e, "load_test")
                print(f"负载测试失败: {e}")
                time.sleep(1)
        
        results = self.monitor.get_stability_metrics()
        results['duration_minutes'] = self.duration_minutes
        results['max_concurrent_operations'] = self.max_concurrent_operations
        
        print(f"负载稳定性测试完成")
        print(f"总耗时: {results['elapsed_time']:.2f}秒")
        print(f"成功率: {results['success_rate']*100:.2f}%")
        print(f"错误率: {results['error_rate']*100:.2f}%")
        print(f"操作/秒: {results['operations_per_second']:.2f}")
        print(f"平均响应时间: {results['avg_response_time']*1000:.2f}毫秒")
        
        return results


class FaultRecoveryTest:
    """故障恢复测试"""
    
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
        self.monitor = StabilityMonitor()
    
    def run(self) -> Dict[str, Any]:
        """运行故障恢复测试"""
        print(f"开始故障恢复测试，迭代次数: {self.iterations}")
        
        for i in range(self.iterations):
            try:
                start_time = time.time()
                
                # 模拟正常操作
                task = Task.create(
                    workorder_id=f"WO-{i:06d}",
                    station_id=1,
                    sn=f"SN-{i:06d}",
                    task_type="test"
                )
                
                # 模拟故障
                if i % 100 == 0:
                    # 模拟任务失败
                    try:
                        task.fail("SIMULATED_ERROR", f"模拟故障 {i}")
                    except Exception as e:
                        # 尝试恢复（只有失败的任务才能重试）
                        try:
                            task.retry()
                        except Exception as retry_error:
                            # 重试也可能失败，这是正常的
                            pass
                
                # 模拟告警
                alarm = Alarm.create(
                    alarm_code=f"ALARM-{i:04d}",
                    alarm_level="warning",
                    message=f"测试告警 {i}",
                    task_id=task.id,
                    station_id="1",
                    device_id=f"DEV-{i:04d}"
                )
                
                # 模拟告警恢复
                alarm.acknowledge(operator_id="OPERATOR-RECOVERY")
                alarm.resolve(operator_id="OPERATOR-RECOVERY")
                
                response_time = time.time() - start_time
                self.monitor.record_success(response_time)
                
            except Exception as e:
                self.monitor.record_failure(e, f"iteration-{i}")
                print(f"故障恢复测试失败: {e}")
        
        results = self.monitor.get_stability_metrics()
        results['iterations'] = self.iterations
        
        print(f"故障恢复测试完成")
        print(f"成功率: {results['success_rate']*100:.2f}%")
        print(f"错误率: {results['error_rate']*100:.2f}%")
        print(f"平均响应时间: {results['avg_response_time']*1000:.2f}毫秒")
        
        return results


def run_all_stability_tests(duration_hours: float = 4.0):
    """运行所有稳定性测试
    
    Args:
        duration_hours: 稳定性测试持续时间（小时）
    """
    print(f"\n{'='*80}")
    print(f"稳定性测试套件 - Stability Test Suite")
    print(f"总持续时间: {duration_hours}小时")
    print(f"{'='*80}\n")
    
    results = {}
    
    # 负载稳定性测试 - 使用指定时间的一半
    load_test = LoadStabilityTest(
        duration_minutes=int(duration_hours * 60 * 0.5),  # 50%时间用于负载测试
        max_concurrent_operations=50
    )
    results['load_stability'] = load_test.run()
    
    # 故障恢复测试
    recovery_test = FaultRecoveryTest(iterations=1000)
    results['fault_recovery'] = recovery_test.run()
    
    return results


if __name__ == '__main__':
    import sys
    
    # 从命令行参数获取持续时间，默认4小时
    duration = 4.0
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            print(f"无效的持续时间参数，使用默认值4小时")
    
    results = run_all_stability_tests(duration_hours=duration)
    print(f"\n{'='*80}")
    print(f"稳定性测试完成 - Stability Tests Completed")
    print(f"{'='*80}")