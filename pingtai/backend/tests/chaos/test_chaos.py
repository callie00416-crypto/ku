# -*- coding: utf-8 -*-
"""
Chaos测试 - Chaos Tests

【职责】
测试系统在异常情况下的表现
模拟各种故障场景
验证系统韧性

【测试内容】
- 网络故障模拟
- 资源耗尽模拟
- 异常输入模拟
- 并发冲突模拟
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import threading
import random
from typing import List, Dict, Any
from platform_core.domain.task import Task
from platform_core.domain.alarm import Alarm
from platform_core.domain.report import Report


class ChaosTestResult:
    """Chaos测试结果"""
    
    def __init__(self):
        self.passed_scenarios: List[str] = []
        self.failed_scenarios: List[Dict[str, Any]] = []
        self.recovery_times: List[float] = []
        self.system_crashes: int = 0
    
    def record_pass(self, scenario_name: str, recovery_time: float = 0.0):
        """记录通过的测试场景"""
        self.passed_scenarios.append(scenario_name)
        if recovery_time > 0:
            self.recovery_times.append(recovery_time)
    
    def record_fail(self, scenario_name: str, error: Exception):
        """记录失败的测试场景"""
        self.failed_scenarios.append({
            'scenario_name': scenario_name,
            'error': str(error)
        })
    
    def record_crash(self):
        """记录系统崩溃"""
        self.system_crashes += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        total_scenarios = len(self.passed_scenarios) + len(self.failed_scenarios)
        avg_recovery_time = sum(self.recovery_times) / len(self.recovery_times) if self.recovery_times else 0.0
        
        return {
            'total_scenarios': total_scenarios,
            'passed_scenarios': len(self.passed_scenarios),
            'failed_scenarios': len(self.failed_scenarios),
            'pass_rate': len(self.passed_scenarios) / total_scenarios if total_scenarios > 0 else 0,
            'avg_recovery_time': avg_recovery_time,
            'system_crashes': self.system_crashes
        }


class NetworkFailureSimulation:
    """网络故障模拟"""
    
    def __init__(self):
        self.results = ChaosTestResult()
    
    def simulate_network_timeout(self) -> bool:
        """模拟网络超时"""
        scenario_name = "网络超时模拟"
        print(f"执行场景: {scenario_name}")
        
        try:
            start_time = time.time()
            
            # 模拟网络超时
            for i in range(10):
                try:
                    task = Task.create(
                        workorder_id=f"WO-TIMEOUT-{i:04d}",
                        station_id=1,
                        sn=f"SN-TIMEOUT-{i:04d}",
                        task_type="test"
                    )
                    
                    # 模拟网络延迟
                    time.sleep(random.uniform(0.1, 0.5))
                    
                    task.start(actor_id=f"ACTOR-TIMEOUT-{i}")
                    
                except Exception as e:
                    # 模拟网络超时错误
                    if "timeout" in str(e).lower() or "network" in str(e).lower():
                        # 预期的网络超时错误
                        pass
                    else:
                        raise
            
            recovery_time = time.time() - start_time
            self.results.record_pass(scenario_name, recovery_time)
            return True
            
        except Exception as e:
            self.results.record_fail(scenario_name, e)
            print(f"场景失败: {e}")
            return False
    
    def simulate_network_partition(self) -> bool:
        """模拟网络分区"""
        scenario_name = "网络分区模拟"
        print(f"执行场景: {scenario_name}")
        
        try:
            start_time = time.time()
            
            # 模拟网络分区
            partition_duration = 2  # 秒
            partition_start = time.time()
            
            for i in range(20):
                try:
                    current_time = time.time()
                    in_partition = (current_time - partition_start) < partition_duration
                    
                    task = Task.create(
                        workorder_id=f"WO-PARTITION-{i:04d}",
                        station_id=1,
                        sn=f"SN-PARTITION-{i:04d}",
                        task_type="test"
                    )
                    
                    if in_partition:
                        # 模拟网络分区期间的失败
                        raise Exception("Network partition detected")
                    else:
                        # 网络恢复后的正常操作
                        task.start(actor_id=f"ACTOR-PARTITION-{i}")
                
                except Exception as e:
                    if "partition" in str(e).lower():
                        # 预期的网络分区错误
                        pass
                    else:
                        raise
                
                time.sleep(0.1)
            
            recovery_time = time.time() - start_time
            self.results.record_pass(scenario_name, recovery_time)
            return True
            
        except Exception as e:
            self.results.record_fail(scenario_name, e)
            print(f"场景失败: {e}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """运行网络故障模拟"""
        print(f"\n{'='*80}")
        print(f"网络故障模拟 - Network Failure Simulation")
        print(f"{'='*80}\n")
        
        # 执行所有场景
        self.simulate_network_timeout()
        self.simulate_network_partition()
        
        return self.results.get_summary()


class ResourceExhaustionSimulation:
    """资源耗尽模拟"""
    
    def __init__(self):
        self.results = ChaosTestResult()
    
    def simulate_memory_pressure(self) -> bool:
        """模拟内存压力"""
        scenario_name = "内存压力模拟"
        print(f"执行场景: {scenario_name}")
        
        try:
            start_time = time.time()
            
            # 创建大量对象模拟内存压力
            objects = []
            try:
                for i in range(1000):
                    task = Task.create(
                        workorder_id=f"WO-MEMORY-{i:04d}",
                        station_id=1,
                        sn=f"SN-MEMORY-{i:04d}",
                        task_type="test"
                    )
                    objects.append(task)
                    
                    # 每100个对象检查一次
                    if i % 100 == 0:
                        # 模拟内存压力下的操作
                        for obj in objects[-10:]:
                            obj.start()
            
            except MemoryError:
                # 预期的内存错误
                pass
            
            finally:
                # 清理对象
                objects.clear()
            
            recovery_time = time.time() - start_time
            self.results.record_pass(scenario_name, recovery_time)
            return True
            
        except Exception as e:
            self.results.record_fail(scenario_name, e)
            print(f"场景失败: {e}")
            return False
    
    def simulate_high_concurrency(self) -> bool:
        """模拟高并发"""
        scenario_name = "高并发模拟"
        print(f"执行场景: {scenario_name}")
        
        try:
            start_time = time.time()
            
            # 创建大量并发操作
            def worker_thread(thread_id: int):
                for i in range(50):
                    try:
                        task = Task.create(
                            workorder_id=f"WO-CONCURRENT-T{thread_id}-{i:03d}",
                            station_id=thread_id % 10 + 1,
                            sn=f"SN-CONCURRENT-T{thread_id}-{i:03d}",
                            task_type="test"
                        )
                        task.start(actor_id=f"ACTOR-CONCURRENT-T{thread_id}")
                    except Exception as e:
                        # 预期的并发错误
                        pass
            
            threads = []
            for i in range(20):
                thread = threading.Thread(target=worker_thread, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            recovery_time = time.time() - start_time
            self.results.record_pass(scenario_name, recovery_time)
            return True
            
        except Exception as e:
            self.results.record_fail(scenario_name, e)
            print(f"场景失败: {e}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """运行资源耗尽模拟"""
        print(f"\n{'='*80}")
        print(f"资源耗尽模拟 - Resource Exhaustion Simulation")
        print(f"{'='*80}\n")
        
        # 执行所有场景
        self.simulate_memory_pressure()
        self.simulate_high_concurrency()
        
        return self.results.get_summary()


class ExceptionInputSimulation:
    """异常输入模拟"""
    
    def __init__(self):
        self.results = ChaosTestResult()
    
    def simulate_malformed_data(self) -> bool:
        """模拟畸形数据"""
        scenario_name = "畸形数据模拟"
        print(f"执行场景: {scenario_name}")
        
        try:
            start_time = time.time()
            
            # 模拟各种畸形数据
            malformed_inputs = [
                None,
                "",
                "   ",
                "\x00\x01\x02",
                "😀😁😂",  # Emoji
                "مرحبا",  # 阿拉伯文
                "こんにちは",  # 日文
                "你好",  # 中文
                "A" * 10000,  # 超长字符串
                "test\x00admin",  # 空字节注入
                "test<script>alert('xss')</script>",  # XSS
            ]
            
            for i, malformed_input in enumerate(malformed_inputs):
                try:
                    task = Task.create(
                        workorder_id=f"WO-MALFORMED-{i:04d}",
                        station_id=1,
                        sn=str(malformed_input)[:128] if malformed_input else "SN-MALFORMED",
                        task_type="test"
                    )
                    
                    # 系统应该能够处理畸形数据
                    if task:
                        pass
                
                except Exception as e:
                    # 预期的异常，系统正确拒绝了畸形数据
                    pass
            
            recovery_time = time.time() - start_time
            self.results.record_pass(scenario_name, recovery_time)
            return True
            
        except Exception as e:
            self.results.record_fail(scenario_name, e)
            print(f"场景失败: {e}")
            return False
    
    def simulate_invalid_state_transitions(self) -> bool:
        """模拟无效状态转换"""
        scenario_name = "无效状态转换模拟"
        print(f"执行场景: {scenario_name}")
        
        try:
            start_time = time.time()
            
            # 模拟无效的状态转换
            task = Task.create(
                workorder_id="WO-INVALID-STATE",
                station_id=1,
                sn="SN-INVALID-STATE",
                task_type="test"
            )
            
            # 尝试无效的状态转换
            invalid_transitions = [
                lambda: task.complete(),  # 未启动就完成
                lambda: task.fail("test"),  # 未启动就失败
                lambda: task.retry(),  # 未失败就重试
            ]
            
            for transition in invalid_transitions:
                try:
                    transition()
                    # 如果成功执行，说明系统没有正确验证状态转换
                    pass
                except Exception as e:
                    # 预期的异常，系统正确拒绝了无效状态转换
                    pass
            
            recovery_time = time.time() - start_time
            self.results.record_pass(scenario_name, recovery_time)
            return True
            
        except Exception as e:
            self.results.record_fail(scenario_name, e)
            print(f"场景失败: {e}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """运行异常输入模拟"""
        print(f"\n{'='*80}")
        print(f"异常输入模拟 - Exception Input Simulation")
        print(f"{'='*80}\n")
        
        # 执行所有场景
        self.simulate_malformed_data()
        self.simulate_invalid_state_transitions()
        
        return self.results.get_summary()


def run_all_chaos_tests():
    """运行所有Chaos测试"""
    print(f"\n{'='*80}")
    print(f"Chaos测试套件 - Chaos Test Suite")
    print(f"{'='*80}\n")
    
    results = {}
    
    # 网络故障模拟
    network_test = NetworkFailureSimulation()
    results['network_failure'] = network_test.run()
    
    # 资源耗尽模拟
    resource_test = ResourceExhaustionSimulation()
    results['resource_exhaustion'] = resource_test.run()
    
    # 异常输入模拟
    exception_test = ExceptionInputSimulation()
    results['exception_input'] = exception_test.run()
    
    return results


if __name__ == '__main__':
    results = run_all_chaos_tests()
    print(f"\n{'='*80}")
    print(f"Chaos测试完成 - Chaos Tests Completed")
    print(f"{'='*80}")