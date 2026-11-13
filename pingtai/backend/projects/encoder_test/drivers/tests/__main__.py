"""
drivers 模块全面测试套件

包含：
- 单元测试：测试各个组件的基本功能
- Mock 测试：测试 Mock 驱动的功能
- 集成测试：测试各层之间的交互
- 系统测试：测试完整的驱动管理流程
"""
import unittest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入各个测试模块
from .unit_tests import UnitTestsSuite
from .mock_tests import MockTestsSuite
from .integration_tests import IntegrationTestsSuite
from .system_tests import SystemTestsSuite


def create_test_suite():
    """创建完整的测试套件"""
    suite = unittest.TestSuite()
    
    # 添加各个测试套件
    suite.addTest(UnitTestsSuite)
    suite.addTest(MockTestsSuite)
    suite.addTest(IntegrationTestsSuite)
    suite.addTest(SystemTestsSuite)
    
    return suite


def run_all_tests():
    """运行所有测试"""
    suite = create_test_suite()
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print(f"\n{'='*50}")
    print(f"测试执行总数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"成功率: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print(f"{'='*50}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)