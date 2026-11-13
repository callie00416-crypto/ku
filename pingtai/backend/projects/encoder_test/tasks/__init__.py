"""
编码器测试系统 - Celery 异步任务
"""
from celery import shared_task
from django.utils import timezone
from ..models import TestTask, TestReport
import subprocess
import json
import os


@shared_task(name='encoder_test.execute_task')
def execute_test_task_async(task_id):
    """
    异步执行测试任务
    """
    try:
        # 获取任务
        task = TestTask.objects.get(id=task_id)
        task.status = 'running'
        task.started_at = timezone.now()
        task.save()
        
        # 获取测试用例
        test_case = task.test_case
        
        # 执行测试（调用 pytest）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(base_dir, test_case.script_path)
        
        # 使用 subprocess 调用 pytest
        cmd = ['python', '-m', 'pytest', script_path, '-v', '--json-report']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        
        # 解析结果
        test_result = {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
        # 保存结果
        task.result = test_result
        task.status = 'passed' if test_result.get('success') else 'failed'
        task.completed_at = timezone.now()
        task.save()
        
        # 生成报告
        report = TestReport.objects.create(
            task=task,
            report_name=f"{test_case.name}_报告_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            report_path=f"reports/{task.id}.json",
            summary={'success': test_result.get('success')}
        )
        
        return {
            'task_id': task_id,
            'status': task.status,
            'result': result
        }
        
    except Exception as e:
        # 记录错误
        task = TestTask.objects.get(id=task_id)
        task.status = 'error'
        task.result = {'error': str(e)}
        task.completed_at = timezone.now()
        task.save()
        
        return {
            'task_id': task_id,
            'status': 'error',
            'error': str(e)
        }


@shared_task(name='encoder_test.stop_task')
def stop_test_task_async(task_id):
    """
    停止测试任务
    """
    try:
        task = TestTask.objects.get(id=task_id)
        task.status = 'stopped'
        task.completed_at = timezone.now()
        task.save()
        
        return {'task_id': task_id, 'status': 'stopped'}
    except Exception as e:
        return {'task_id': task_id, 'error': str(e)}


def execute_test_task(task_id):
    """
    同步执行测试任务（用于 Redis 不可用时的降级方案）
    """
    try:
        # 获取任务
        task = TestTask.objects.get(id=task_id)
        task.status = 'running'
        task.started_at = timezone.now()
        task.save()
        
        # 获取测试用例
        test_case = task.test_case
        
        # 执行测试（调用 pytest）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(base_dir, test_case.script_path)
        
        # 使用 subprocess 调用 pytest
        cmd = ['python', '-m', 'pytest', script_path, '-v', '--json-report']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        
        # 解析结果
        test_result = {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
        # 保存结果
        task.result = test_result
        task.status = 'passed' if test_result.get('success') else 'failed'
        task.completed_at = timezone.now()
        task.save()
        
        # 生成报告
        report = TestReport.objects.create(
            task=task,
            report_name=f"{test_case.name}_报告_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            report_path=f"reports/{task.id}.json",
            summary={'success': test_result.get('success')}
        )
        
        return {
            'task_id': task_id,
            'status': task.status,
            'result': test_result
        }
        
    except Exception as e:
        # 记录错误
        try:
            task = TestTask.objects.get(id=task_id)
            task.status = 'error'
            task.result = {'error': str(e)}
            task.completed_at = timezone.now()
            task.save()
        except:
            pass
        
        return {
            'task_id': task_id,
            'status': 'error',
            'error': str(e)
        }