# -*- coding: utf-8 -*-
"""
综合压力测试 - Comprehensive Stress Tests

【职责】
综合压力测试
验证系统在极限条件下的表现
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径（必须在导入platform之前）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 确保使用项目的platform包，而不是Python内置的platform模块
if 'platform_core' in sys.modules:
    del sys.modules['platform_core']

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