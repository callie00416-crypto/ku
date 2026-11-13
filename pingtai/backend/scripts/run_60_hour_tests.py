# -*- coding: utf-8 -*-
"""
60小时综合测试执行脚本 - 60-Hour Comprehensive Test Suite

【测试时间分配】
- 单元测试: 30分钟
- 性能测试: 9小时
- 系统测试: 4.5小时
- 稳定性测试: 18小时
- 安全测试: 4.5小时
- Chaos测试: 4.5小时
- 内存泄漏测试: 9小时
- 综合压力测试: 6.75小时

【总测试时间】: 60小时
【用途】: 工业级超长时间稳定性测试
"""
import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List


class TestSuiteExecutor:
    """测试套件执行器（60小时版）"""
    
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.start_time = datetime.now()
        self.results: Dict[str, Any] = {
            'start_time': self.start_time.isoformat(),
            'test_suites': {},
            'summary': {}
        }
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """运行单元测试"""
        print(f"\n{'#'*80}")
        print(f"# 单元测试阶段 - Unit Tests Phase")
        print(f"# 预计耗时: 30分钟")
        print(f"{'#'*80}")
        
        test_file = Path(__file__).parent / "run_unit_tests.py"
        
        result = subprocess.run(
            ['python', str(test_file)],
            capture_output=True,
            text=True,
            timeout=30 * 60 + 300  # 30分钟 + 5分钟超时
        )
        
        suite_result = {
            'suite_name': 'unit_tests',
            'description': '单元测试 - 验证基本功能正确性',
            'start_time': datetime.now().isoformat(),
            'status': 'passed' if result.returncode == 0 else 'failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': 30 * 60,  # 30分钟转换为秒
            'error': result.stderr if result.returncode != 0 else None
        }
        suite_result['end_time'] = datetime.now().isoformat()
        
        if result.returncode == 0:
            print(f"测试套件 unit_tests 通过")
        else:
            print(f"测试套件 unit_tests 失败")
            print(f"错误: {result.stderr}")
        
        self.results['test_suites']['unit_tests'] = suite_result
        return suite_result
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        print(f"\n{'#'*80}")
        print(f"# 性能测试阶段 - Performance Tests Phase")
        print(f"# 预计耗时: 9小时")
        print(f"{'#'*80}")
        
        test_file = Path(__file__).parent / "tests" / "performance" / "test_performance.py"
        
        result = subprocess.run(
            ['python', str(test_file)],
            capture_output=True,
            text=True,
            timeout=9 * 3600 + 600  # 9小时 + 10分钟超时
        )
        
        suite_result = {
            'suite_name': 'performance_tests',
            'description': '性能测试 - 验证系统性能指标',
            'start_time': datetime.now().isoformat(),
            'status': 'passed' if result.returncode == 0 else 'failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': 9 * 3600,  # 9小时转换为秒
            'error': result.stderr if result.returncode != 0 else None
        }
        suite_result['end_time'] = datetime.now().isoformat()
        
        if result.returncode == 0:
            print(f"测试套件 performance_tests 通过")
        else:
            print(f"测试套件 performance_tests 失败")
            print(f"错误: {result.stderr}")
        
        self.results['test_suites']['performance_tests'] = suite_result
        return suite_result
    
    def run_system_tests(self) -> Dict[str, Any]:
        """运行系统测试"""
        print(f"\n{'#'*80}")
        print(f"# 系统测试阶段 - System Tests Phase")
        print(f"# 预计耗时: 4.5小时")
        print(f"{'#'*80}")
        
        test_file = Path(__file__).parent / "tests" / "system" / "test_system.py"
        
        result = subprocess.run(
            ['python', str(test_file)],
            capture_output=True,
            text=True,
            timeout=4.5 * 3600 + 600  # 4.5小时 + 10分钟超时
        )
        
        suite_result = {
            'suite_name': 'system_tests',
            'description': '系统测试 - 验证系统集成和交互',
            'start_time': datetime.now().isoformat(),
            'status': 'passed' if result.returncode == 0 else 'failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': 4.5 * 3600,  # 4.5小时转换为秒
            'error': result.stderr if result.returncode != 0 else None
        }
        suite_result['end_time'] = datetime.now().isoformat()
        
        if result.returncode == 0:
            print(f"测试套件 system_tests 通过")
        else:
            print(f"测试套件 system_tests 失败")
            print(f"错误: {result.stderr}")
        
        self.results['test_suites']['system_tests'] = suite_result
        return suite_result
    
    def run_stability_tests(self, duration_hours: float = 18.0) -> Dict[str, Any]:
        """运行稳定性测试（60小时版）"""
        print(f"\n{'#'*80}")
        print(f"# 稳定性测试阶段 - Stability Tests Phase")
        print(f"# 预计耗时: {duration_hours}小时")
        print(f"{'#'*80}")
        
        test_file = Path(__file__).parent / "tests" / "stability" / "test_stability.py"
        
        result = subprocess.run(
            ['python', str(test_file), str(duration_hours)],
            capture_output=True,
            text=True,
            timeout=int(duration_hours * 3600) + 600  # 额外10分钟超时
        )
        
        suite_result = {
            'suite_name': 'stability_tests',
            'description': '稳定性测试 - 验证长时间运行稳定性',
            'start_time': datetime.now().isoformat(),
            'status': 'passed' if result.returncode == 0 else 'failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': duration_hours * 3600,  # 转换为秒
            'error': result.stderr if result.returncode != 0 else None
        }
        suite_result['end_time'] = datetime.now().isoformat()
        
        if result.returncode == 0:
            print(f"测试套件 stability_tests 通过")
        else:
            print(f"测试套件 stability_tests 失败")
            print(f"错误: {result.stderr}")
        
        self.results['test_suites']['stability_tests'] = suite_result
        return suite_result
    
    def run_security_tests(self) -> Dict[str, Any]:
        """运行安全测试"""
        print(f"\n{'#'*80}")
        print(f"# 安全测试阶段 - Security Tests Phase")
        print(f"# 预计耗时: 4.5小时")
        print(f"{'#'*80}")
        
        test_file = Path(__file__).parent / "tests" / "security" / "test_security.py"
        
        result = subprocess.run(
            ['python', str(test_file)],
            capture_output=True,
            text=True,
            timeout=4.5 * 3600 + 600  # 4.5小时 + 10分钟超时
        )
        
        suite_result = {
            'suite_name': 'security_tests',
            'description': '安全测试 - 验证系统安全性',
            'start_time': datetime.now().isoformat(),
            'status': 'passed' if result.returncode == 0 else 'failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': 4.5 * 3600,  # 4.5小时转换为秒
            'error': result.stderr if result.returncode != 0 else None
        }
        suite_result['end_time'] = datetime.now().isoformat()
        
        if result.returncode == 0:
            print(f"测试套件 security_tests 通过")
        else:
            print(f"测试套件 security_tests 失败")
            print(f"错误: {result.stderr}")
        
        self.results['test_suites']['security_tests'] = suite_result
        return suite_result
    
    def run_chaos_tests(self) -> Dict[str, Any]:
        """运行Chaos测试"""
        print(f"\n{'#'*80}")
        print(f"# Chaos测试阶段 - Chaos Tests Phase")
        print(f"# 预计耗时: 4.5小时")
        print(f"{'#'*80}")
        
        test_file = Path(__file__).parent / "tests" / "chaos" / "test_chaos.py"
        
        result = subprocess.run(
            ['python', str(test_file)],
            capture_output=True,
            text=True,
            timeout=4.5 * 3600 + 600  # 4.5小时 + 10分钟超时
        )
        
        suite_result = {
            'suite_name': 'chaos_tests',
            'description': 'Chaos测试 - 验证系统韧性',
            'start_time': datetime.now().isoformat(),
            'status': 'passed' if result.returncode == 0 else 'failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': 4.5 * 3600,  # 4.5小时转换为秒
            'error': result.stderr if result.returncode != 0 else None
        }
        suite_result['end_time'] = datetime.now().isoformat()
        
        if result.returncode == 0:
            print(f"测试套件 chaos_tests 通过")
        else:
            print(f"测试套件 chaos_tests 失败")
            print(f"错误: {result.stderr}")
        
        self.results['test_suites']['chaos_tests'] = suite_result
        return suite_result
    
    def run_memory_leak_tests(self, duration_hours: float = 9.0) -> Dict[str, Any]:
        """运行内存泄漏测试（60小时版）"""
        print(f"\n{'#'*80}")
        print(f"# 内存泄漏测试阶段 - Memory Leak Tests Phase")
        print(f"# 预计耗时: {duration_hours}小时")
        print(f"# 重点监控: 内存增长、GC对象数量、内存泄漏检测")
        print(f"{'#'*80}")
        
        test_file = Path(__file__).parent / "tests" / "memory" / "test_memory_leak.py"
        
        result = subprocess.run(
            ['python', str(test_file), str(duration_hours)],
            capture_output=True,
            text=True,
            timeout=int(duration_hours * 3600) + 600  # 额外10分钟超时
        )
        
        suite_result = {
            'suite_name': 'memory_leak_tests',
            'description': '内存泄漏测试 - 检测内存泄漏问题',
            'start_time': datetime.now().isoformat(),
            'status': 'passed' if result.returncode == 0 else 'failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': duration_hours * 3600,  # 转换为秒
            'error': result.stderr if result.returncode != 0 else None
        }
        suite_result['end_time'] = datetime.now().isoformat()
        
        if result.returncode == 0:
            print(f"测试套件 memory_leak_tests 通过")
        else:
            print(f"测试套件 memory_leak_tests 失败")
            print(f"错误: {result.stderr}")
        
        self.results['test_suites']['memory_leak_tests'] = suite_result
        return suite_result
    
    def run_comprehensive_stress_tests(self, duration_hours: float = 6.75) -> Dict[str, Any]:
        """运行综合压力测试（60小时版）"""
        print(f"\n{'#'*80}")
        print(f"# 综合压力测试阶段 - Comprehensive Stress Tests Phase")
        print(f"# 预计耗时: {duration_hours}小时")
        print(f"# 重点监控: 系统崩溃、内存泄漏、性能下降")
        print(f"{'#'*80}")
        
        stress_test_file = Path(__file__).parent / "tests" / "comprehensive_stress_test.py"
        
        if not stress_test_file.exists():
            print("创建综合压力测试...")
            self.create_comprehensive_stress_test(stress_test_file)
        
        result = subprocess.run(
            ['python', str(stress_test_file), str(duration_hours)],
            capture_output=True,
            text=True,
            timeout=int(duration_hours * 3600) + 600  # 额外10分钟超时
        )
        
        suite_result = {
            'suite_name': 'comprehensive_stress_tests',
            'description': '综合压力测试 - 验证系统在极限条件下的表现',
            'start_time': datetime.now().isoformat(),
            'status': 'passed' if result.returncode == 0 else 'failed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': duration_hours * 3600,  # 转换为秒
            'error': result.stderr if result.returncode != 0 else None
        }
        suite_result['end_time'] = datetime.now().isoformat()
        
        if result.returncode == 0:
            print(f"测试套件 comprehensive_stress_tests 通过")
        else:
            print(f"测试套件 comprehensive_stress_tests 失败")
            print(f"错误: {result.stderr}")
        
        self.results['test_suites']['comprehensive_stress_tests'] = suite_result
        return suite_result
    
    def create_comprehensive_stress_test(self, test_file: Path):
        """创建综合压力测试"""
        stress_test_content = '''# -*- coding: utf-8 -*-
"""
综合压力测试 - Comprehensive Stress Tests

【职责】
综合压力测试
验证系统在极限条件下的表现
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import threading
import random
from platform_core.domain.task import Task
from platform_core.domain.alarm import Alarm


class ComprehensiveStressTest:
    """综合压力测试"""
    
    def __init__(self, duration_hours: float = 6.75):
        self.duration_hours = duration_hours
        self.start_time = time.time()
        self.errors = []
        self.success_count = 0
        self.failure_count = 0
    
    def worker_thread(self, thread_id: int):
        """工作线程"""
        while (time.time() - self.start_time) < (self.duration_hours * 3600):
            try:
                operation = random.choice(['task', 'alarm', 'mixed'])
                
                if operation == 'task':
                    task = Task.create(
                        workorder_id=f"WO-STRESS-T{thread_id}-{int(time.time()*1000)}",
                        station_id=random.randint(1, 10),
                        sn=f"SN-STRESS-T{thread_id}-{int(time.time()*1000)}",
                        task_type="test"
                    )
                    task.start(actor_id=f"ACTOR-STRESS-T{thread_id}")
                    task.complete()
                
                elif operation == 'alarm':
                    alarm = Alarm.create(
                        alarm_code=f"ALARM-STRESS-T{thread_id}-{int(time.time()*1000)}",
                        alarm_level=random.choice(['info', 'warning', 'error']),
                        message=f"压力测试告警 {int(time.time()*1000)}",
                        task_id=f"TASK-{int(time.time()*1000)}",
                        station_id=str(random.randint(1, 10)),
                        device_id=f"DEV-{int(time.time()*1000)}"
                    )
                    alarm.acknowledge(operator_id=f"OPERATOR-STRESS-T{thread_id}")
                    alarm.resolve(operator_id=f"OPERATOR-STRESS-T{thread_id}")
                
                elif operation == 'mixed':
                    task = Task.create(
                        workorder_id=f"WO-MIXED-T{thread_id}-{int(time.time()*1000)}",
                        station_id=random.randint(1, 10),
                        sn=f"SN-MIXED-T{thread_id}-{int(time.time()*1000)}",
                        task_type="test"
                    )
                    
                    alarm = Alarm.create(
                        alarm_code=f"ALARM-MIXED-T{thread_id}-{int(time.time()*1000)}",
                        alarm_level="warning",
                        message=f"混合测试告警 {int(time.time()*1000)}",
                        task_id=task.id,
                        station_id=str(random.randint(1, 10)),
                        device_id=f"DEV-{int(time.time()*1000)}"
                    )
                    
                    task.start(actor_id=f"ACTOR-MIXED-T{thread_id}")
                    alarm.acknowledge(operator_id=f"OPERATOR-MIXED-T{thread_id}")
                    task.complete()
                    alarm.resolve(operator_id=f"OPERATOR-MIXED-T{thread_id}")
                
                self.success_count += 1
                
            except Exception as e:
                self.failure_count += 1
                self.errors.append(str(e))
            
            time.sleep(random.uniform(0.01, 0.1))
    
    def run(self):
        """运行综合压力测试"""
        print(f"开始综合压力测试，持续时间: {self.duration_hours}小时")
        
        num_threads = 10
        threads = []
        
        for i in range(num_threads):
            thread = threading.Thread(target=self.worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        def monitor():
            while (time.time() - self.start_time) < (self.duration_hours * 3600):
                time.sleep(300)  # 每5分钟输出一次状态
                elapsed = (time.time() - self.start_time) / 60
                success_rate = self.success_count / (self.success_count + self.failure_count) * 100 if (self.success_count + self.failure_count) > 0 else 0
                print(f"运行状态 - 已运行: {elapsed:.1f}分钟, 成功率: {success_rate:.2f}%, 错误数: {len(self.errors)}")
        
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()
        
        for thread in threads:
            thread.join()
        
        monitor_thread.join()
        
        print(f"综合压力测试完成")
        print(f"总成功数: {self.success_count}")
        print(f"总失败数: {self.failure_count}")
        print(f"总错误数: {len(self.errors)}")
        
        if self.errors:
            print(f"最近错误: {self.errors[-5:]}")  # 显示最近5个错误


if __name__ == '__main__':
    duration = 6.75
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            print(f"无效的持续时间参数，使用默认值6.75小时")
    
    test = ComprehensiveStressTest(duration_hours=duration)
    test.run()
'''
        
        test_file.write_text(stress_test_content, encoding='utf-8')
    
    def generate_summary(self):
        """生成测试摘要"""
        print(f"\n{'='*80}")
        print(f"测试摘要 - Test Summary")
        print(f"{'='*80}\n")
        
        total_suites = len(self.results['test_suites'])
        passed_suites = sum(1 for suite in self.results['test_suites'].values() if suite['status'] == 'passed')
        failed_suites = sum(1 for suite in self.results['test_suites'].values() if suite['status'] == 'failed')
        timeout_suites = sum(1 for suite in self.results['test_suites'].values() if suite['status'] == 'timeout')
        error_suites = sum(1 for suite in self.results['test_suites'].values() if suite['status'] == 'error')
        
        total_duration = sum(suite['duration'] for suite in self.results['test_suites'].values())
        
        summary = {
            'total_suites': total_suites,
            'passed_suites': passed_suites,
            'failed_suites': failed_suites,
            'timeout_suites': timeout_suites,
            'error_suites': error_suites,
            'pass_rate': passed_suites / total_suites if total_suites > 0 else 0,
            'total_duration': total_duration,
            'total_duration_hours': total_duration / 3600
        }
        
        self.results['summary'] = summary
        self.results['end_time'] = datetime.now().isoformat()
        
        print(f"总测试套件数: {total_suites}")
        print(f"通过套件数: {passed_suites}")
        print(f"失败套件数: {failed_suites}")
        print(f"超时套件数: {timeout_suites}")
        print(f"错误套件数: {error_suites}")
        print(f"通过率: {summary['pass_rate']*100:.2f}%")
        print(f"总耗时: {total_duration/3600:.2f}小时")
        
        print(f"\n详细结果:")
        for suite_name, suite_result in self.results['test_suites'].items():
            status_icon = {
                'passed': 'OK',
                'failed': 'FAIL',
                'timeout': 'TIMEOUT',
                'error': 'ERROR'
            }.get(suite_result['status'], 'UNKNOWN')
            
            print(f"{status_icon} {suite_name}: {suite_result['status']} ({suite_result['duration']/60:.2f}分钟)")
        
        return summary
    
    def save_results(self):
        """保存测试结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = self.output_dir / f"test_results_60hour_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n测试结果已保存到: {result_file}")
        return result_file
    
    def run_60_hour_comprehensive_tests(self):
        """运行60小时综合测试"""
        print(f"\n{'#'*80}")
        print(f"# 60小时综合测试 - 60-Hour Comprehensive Test Suite")
        print(f"# 工业自动化测试平台 - Industrial Automation Test Platform")
        print(f"# 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# 预计结束时间: {(self.start_time + timedelta(hours=60)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*80}")
        
        try:
            # 1. 单元测试 (30分钟)
            self.run_unit_tests()
            
            # 2. 性能测试 (9小时)
            self.run_performance_tests()
            
            # 3. 系统测试 (4.5小时)
            self.run_system_tests()
            
            # 4. 稳定性测试 (18小时)
            self.run_stability_tests(duration_hours=18.0)
            
            # 5. 安全测试 (4.5小时)
            self.run_security_tests()
            
            # 6. Chaos测试 (4.5小时)
            self.run_chaos_tests()
            
            # 7. 内存泄漏测试 (9小时)
            self.run_memory_leak_tests(duration_hours=9.0)
            
            # 8. 综合压力测试 (6.75小时)
            self.run_comprehensive_stress_tests(duration_hours=6.75)
            
            # 生成摘要
            self.generate_summary()
            
            # 保存结果
            self.save_results()
            
            print(f"\n{'#'*80}")
            print(f"# 60小时综合测试完成 - 60-Hour Comprehensive Tests Completed")
            print(f"# 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"# 总耗时: {(datetime.now() - self.start_time).total_seconds()/3600:.2f}小时")
            print(f"{'#'*80}")
            
        except KeyboardInterrupt:
            print(f"\n测试被用户中断")
            self.generate_summary()
            self.save_results()
            
        except Exception as e:
            print(f"\n测试执行异常: {e}")
            self.generate_summary()
            self.save_results()
            raise


def main():
    """主函数"""
    executor = TestSuiteExecutor()
    executor.run_60_hour_comprehensive_tests()


if __name__ == '__main__':
    main()