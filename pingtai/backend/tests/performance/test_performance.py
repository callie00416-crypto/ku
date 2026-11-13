# -*- coding: utf-8 -*-
"""
性能测试 - Performance Tests

【职责】
测试系统性能指标
包括响应时间、吞吐量、并发能力等

【测试内容】
- 任务创建性能
- 告警处理性能
- 报告生成性能
- 并发处理能力
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import threading
import statistics
from typing import List, Dict, Any
from platform_core.domain.task import Task
from platform_core.domain.alarm import Alarm
from platform_core.domain.report import Report


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.throughput: List[float] = []
        self.error_count: int = 0
        self.success_count: int = 0
    
    def add_response_time(self, response_time: float):
        """添加响应时间"""
        self.response_times.append(response_time)
    
    def add_throughput(self, operations_per_second: float):
        """添加吞吐量"""
        self.throughput.append(operations_per_second)
    
    def record_success(self):
        """记录成功"""
        self.success_count += 1
    
    def record_error(self):
        """记录错误"""
        self.error_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.response_times:
            return {
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'median_response_time': 0,
                'p95_response_time': 0,
                'p99_response_time': 0,
                'avg_throughput': 0,
                'error_rate': 0,
                'total_operations': 0
            }
        
        sorted_times = sorted(self.response_times)
        total_operations = self.success_count + self.error_count
        
        return {
            'avg_response_time': statistics.mean(self.response_times),
            'min_response_time': min(self.response_times),
            'max_response_time': max(self.response_times),
            'median_response_time': statistics.median(self.response_times),
            'p95_response_time': sorted_times[int(len(sorted_times) * 0.95)],
            'p99_response_time': sorted_times[int(len(sorted_times) * 0.99)],
            'avg_throughput': statistics.mean(self.throughput) if self.throughput else 0,
            'error_rate': self.error_count / total_operations if total_operations > 0 else 0,
            'total_operations': total_operations
        }


class TaskCreationPerformanceTest:
    """任务创建性能测试"""
    
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
        self.metrics = PerformanceMetrics()
    
    def run(self) -> Dict[str, Any]:
        """运行性能测试"""
        print(f"开始任务创建性能测试，迭代次数: {self.iterations}")
        
        start_time = time.time()
        
        for i in range(self.iterations):
            try:
                iteration_start = time.time()
                
                task = Task.create(
                    workorder_id=f"WO-{i:06d}",
                    station_id=1,
                    sn=f"SN-{i:06d}",
                    task_type="test"
                )
                
                iteration_time = time.time() - iteration_start
                self.metrics.add_response_time(iteration_time)
                self.metrics.record_success()
                
            except Exception as e:
                self.metrics.record_error()
                print(f"任务创建失败: {e}")
        
        total_time = time.time() - start_time
        throughput = self.iterations / total_time
        self.metrics.add_throughput(throughput)
        
        results = self.metrics.get_statistics()
        results['total_time'] = total_time
        results['throughput'] = throughput
        
        print(f"任务创建性能测试完成")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"吞吐量: {throughput:.2f}操作/秒")
        print(f"平均响应时间: {results['avg_response_time']*1000:.2f}毫秒")
        print(f"错误率: {results['error_rate']*100:.2f}%")
        
        return results


class AlarmProcessingPerformanceTest:
    """告警处理性能测试"""
    
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
        self.metrics = PerformanceMetrics()
    
    def run(self) -> Dict[str, Any]:
        """运行性能测试"""
        print(f"开始告警处理性能测试，迭代次数: {self.iterations}")
        
        start_time = time.time()
        
        for i in range(self.iterations):
            try:
                iteration_start = time.time()
                
                alarm = Alarm.create(
                    alarm_code=f"ALARM-{i:04d}",
                    alarm_level="warning",
                    message=f"测试告警 {i}",
                    task_id=f"TASK-{i:06d}",
                    station_id="1",
                    device_id=f"DEV-{i:04d}"
                )
                
                alarm.acknowledge(operator_id="OPERATOR-PERF")
                alarm.resolve(operator_id="OPERATOR-PERF")
                
                iteration_time = time.time() - iteration_start
                self.metrics.add_response_time(iteration_time)
                self.metrics.record_success()
                
            except Exception as e:
                self.metrics.record_error()
                print(f"告警处理失败: {e}")
        
        total_time = time.time() - start_time
        throughput = self.iterations / total_time
        self.metrics.add_throughput(throughput)
        
        results = self.metrics.get_statistics()
        results['total_time'] = total_time
        results['throughput'] = throughput
        
        print(f"告警处理性能测试完成")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"吞吐量: {throughput:.2f}操作/秒")
        print(f"平均响应时间: {results['avg_response_time']*1000:.2f}毫秒")
        print(f"错误率: {results['error_rate']*100:.2f}%")
        
        return results


class ReportGenerationPerformanceTest:
    """报告生成性能测试"""
    
    def __init__(self, iterations: int = 100):
        self.iterations = iterations
        self.metrics = PerformanceMetrics()
    
    def run(self) -> Dict[str, Any]:
        """运行性能测试"""
        print(f"开始报告生成性能测试，迭代次数: {self.iterations}")
        
        start_time = time.time()
        
        for i in range(self.iterations):
            try:
                iteration_start = time.time()
                
                task = Task.create(
                    workorder_id=f"WO-{i:06d}",
                    station_id=1,
                    sn=f"SN-{i:06d}",
                    task_type="test"
                )
                
                report = Report.create(
                    task_id=task.id,
                    workorder_id=f"WO-{i:06d}",
                    sn=f"SN-{i:06d}"
                )
                
                iteration_time = time.time() - iteration_start
                self.metrics.add_response_time(iteration_time)
                self.metrics.record_success()
                
            except Exception as e:
                self.metrics.record_error()
                print(f"报告生成失败: {e}")
        
        total_time = time.time() - start_time
        throughput = self.iterations / total_time
        self.metrics.add_throughput(throughput)
        
        results = self.metrics.get_statistics()
        results['total_time'] = total_time
        results['throughput'] = throughput
        
        print(f"报告生成性能测试完成")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"吞吐量: {throughput:.2f}操作/秒")
        print(f"平均响应时间: {results['avg_response_time']*1000:.2f}毫秒")
        print(f"错误率: {results['error_rate']*100:.2f}%")
        
        return results


class ConcurrencyPerformanceTest:
    """并发性能测试"""
    
    def __init__(self, threads: int = 10, operations_per_thread: int = 100):
        self.threads = threads
        self.operations_per_thread = operations_per_thread
        self.metrics = PerformanceMetrics()
    
    def worker_thread(self, thread_id: int):
        """工作线程"""
        for i in range(self.operations_per_thread):
            try:
                iteration_start = time.time()
                
                task = Task.create(
                    workorder_id=f"WO-T{thread_id:02d}-{i:04d}",
                    station_id=thread_id,
                    sn=f"SN-T{thread_id:02d}-{i:04d}",
                    task_type="test"
                )
                
                iteration_time = time.time() - iteration_start
                self.metrics.add_response_time(iteration_time)
                self.metrics.record_success()
                
            except Exception as e:
                self.metrics.record_error()
                print(f"线程{thread_id}操作失败: {e}")
    
    def run(self) -> Dict[str, Any]:
        """运行并发性能测试"""
        print(f"开始并发性能测试，线程数: {self.threads}，每线程操作数: {self.operations_per_thread}")
        
        start_time = time.time()
        
        threads = []
        for i in range(self.threads):
            thread = threading.Thread(target=self.worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        total_operations = self.threads * self.operations_per_thread
        throughput = total_operations / total_time
        self.metrics.add_throughput(throughput)
        
        results = self.metrics.get_statistics()
        results['total_time'] = total_time
        results['throughput'] = throughput
        results['threads'] = self.threads
        results['operations_per_thread'] = self.operations_per_thread
        
        print(f"并发性能测试完成")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"总操作数: {total_operations}")
        print(f"吞吐量: {throughput:.2f}操作/秒")
        print(f"平均响应时间: {results['avg_response_time']*1000:.2f}毫秒")
        print(f"错误率: {results['error_rate']*100:.2f}%")
        
        return results


def run_all_performance_tests():
    """运行所有性能测试"""
    print(f"\n{'='*80}")
    print(f"性能测试套件 - Performance Test Suite")
    print(f"{'='*80}\n")
    
    results = {}
    
    # 任务创建性能测试
    task_test = TaskCreationPerformanceTest(iterations=1000)
    results['task_creation'] = task_test.run()
    
    # 告警处理性能测试
    alarm_test = AlarmProcessingPerformanceTest(iterations=1000)
    results['alarm_processing'] = alarm_test.run()
    
    # 报告生成性能测试
    report_test = ReportGenerationPerformanceTest(iterations=100)
    results['report_generation'] = report_test.run()
    
    # 并发性能测试
    concurrency_test = ConcurrencyPerformanceTest(threads=10, operations_per_thread=100)
    results['concurrency'] = concurrency_test.run()
    
    return results


if __name__ == '__main__':
    results = run_all_performance_tests()
    print(f"\n{'='*80}")
    print(f"性能测试完成 - Performance Tests Completed")
    print(f"{'='*80}")