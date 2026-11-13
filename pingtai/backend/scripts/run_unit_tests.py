# -*- coding: utf-8 -*-
"""
单元测试执行脚本 - Unit Test Execution Script

【职责】
统一执行平台层和项目层的单元测试
提供测试结果汇总

【使用方法】
python run_unit_tests.py

【测试范围】
- 平台层测试：任务、告警、报告、领域模型
- 项目层测试：驱动、测试引擎、测试用例
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_python_path():
    """设置Python路径"""
    backend_root = Path(__file__).parent
    sys.path.insert(0, str(backend_root))
    os.environ['PYTHONPATH'] = str(backend_root)

def run_test_file(test_file_path, description):
    """运行单个测试文件
    
    Args:
        test_file_path: 测试文件路径
        description: 测试描述
        
    Returns:
        测试结果
    """
    print(f"\n{'='*80}")
    print(f"运行测试: {description}")
    print(f"测试文件: {test_file_path}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            ['python', str(test_file_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"[PASS] 测试通过: {description}")
            return True
        else:
            print(f"[FAIL] 测试失败: {description}")
            print(f"错误输出:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] 测试超时: {description}")
        return False
    except Exception as e:
        print(f"[ERROR] 测试异常: {description}")
        print(f"异常信息: {str(e)}")
        return False

def run_platform_tests():
    """运行平台层测试"""
    print(f"\n{'#'*80}")
    print(f"# 平台层测试 - Platform Layer Tests")
    print(f"{'#'*80}")
    
    test_files = [
        ('platform/domain/task/test_task.py', '任务领域测试'),
        ('platform/domain/alarm/test_alarm.py', '告警领域测试'),
        ('platform/domain/report/test_report.py', '报告领域测试'),
        ('platform/domain/tests/test_domain_models.py', '领域模型综合测试'),
    ]
    
    results = []
    for test_file, description in test_files:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            result = run_test_file(test_path, description)
            results.append((description, result))
        else:
            print(f"[WARN] 测试文件不存在: {test_file}")
            results.append((description, False))
    
    return results

def run_project_tests():
    """运行项目层测试"""
    print(f"\n{'#'*80}")
    print(f"# 项目层测试 - Project Layer Tests")
    print(f"{'#'*80}")
    
    test_files = [
        ('projects/encoder_test/core/testcase/base/test_config.py', '测试配置测试'),
    ]
    
    results = []
    for test_file, description in test_files:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            result = run_test_file(test_path, description)
            results.append((description, result))
        else:
            print(f"⚠️ 测试文件不存在: {test_file}")
            results.append((description, False))
    
    return results

def print_summary(platform_results, project_results):
    """打印测试结果汇总
    
    Args:
        platform_results: 平台层测试结果
        project_results: 项目层测试结果
    """
    print(f"\n{'#'*80}")
    print(f"# 测试结果汇总 - Test Summary")
    print(f"{'#'*80}")
    
    print(f"\n## 平台层测试结果")
    platform_passed = sum(1 for _, result in platform_results if result)
    platform_total = len(platform_results)
    print(f"通过: {platform_passed}/{platform_total}")
    
    for description, result in platform_results:
        status = "[PASS] 通过" if result else "[FAIL] 失败"
        print(f"  {status}: {description}")
    
    print(f"\n## 项目层测试结果")
    project_passed = sum(1 for _, result in project_results if result)
    project_total = len(project_results)
    print(f"通过: {project_passed}/{project_total}")
    
    for description, result in project_results:
        status = "[PASS] 通过" if result else "[FAIL] 失败"
        print(f"  {status}: {description}")
    
    print(f"\n## 总体结果")
    total_passed = platform_passed + project_passed
    total_tests = platform_total + project_total
    print(f"总通过: {total_passed}/{total_tests}")
    print(f"通过率: {total_passed/total_tests*100:.1f}%")
    
    if total_passed == total_tests:
        print(f"\n[SUCCESS] 所有测试通过！")
    else:
        print(f"\n⚠️ 部分测试失败，请检查测试输出")

def main():
    """主函数"""
    print(f"\n{'#'*80}")
    print(f"# 工业自动化测试平台 - 单元测试执行")
    print(f"# Industrial Automation Test Platform - Unit Test Execution")
    print(f"{'#'*80}")
    
    # 设置Python路径
    setup_python_path()
    
    # 运行平台层测试
    platform_results = run_platform_tests()
    
    # 运行项目层测试
    project_results = run_project_tests()
    
    # 打印测试结果汇总
    print_summary(platform_results, project_results)

if __name__ == '__main__':
    main()