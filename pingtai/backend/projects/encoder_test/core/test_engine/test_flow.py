"""
测试流程编排 - 负责管理测试任务的整体流程
"""
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from .test_executor import Executor, Status
from projects.encoder_test.drivers.driver_manager import DriverManager
from projects.encoder_test.utils.result_builder import ResultBuilder, TestResult, TestSummary


# 向后兼容别名
TestExecutor = Executor
TestStatus = Status


class Flow:
    """测试流程"""
    
    def __init__(self, product_sn: str, station_id: int, config_path: str = None):
        """
        Args:
            product_sn: 产品SN码
            station_id: 工位ID
            config_path: 配置文件路径
        """
        self.product_sn = product_sn
        self.station_id = station_id
        self.config_path = config_path
        
        # 初始化驱动管理器
        self.driver_manager = DriverManager(config_path)
        
        # 测试用例列表
        self.test_cases: List[Dict[str, Any]] = []
        
        # 测试结果
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        self.status = Status.PENDING
    
    def add_test_case(self, case_code: str, case_name: str, test_func: callable, params: Dict = None):
        """
        添加测试用例
        
        Args:
            case_code: 用例编号
            case_name: 用例名称
            test_func: 测试函数
            params: 测试参数
        """
        self.test_cases.append({
            'case_code': case_code,
            'case_name': case_name,
            'test_func': test_func,
            'params': params or {}
        })
    
    def start(self) -> Dict[str, Any]:
        """
        开始测试流程
        
        Returns:
            测试结果汇总
        """
        self.start_time = datetime.now()
        self.status = Status.RUNNING
        
        # 连接所有驱动
        if not self.driver_manager.connect_all():
            return ResultBuilder.create_summary(
                product_sn=self.product_sn,
                station_id=self.station_id,
                error="驱动连接失败",
                start_time=self.start_time
            ).to_dict()
        
        # 执行所有测试用例
        for case in self.test_cases:
            executor = Executor(case, self.driver_manager)
            result_dict = executor.execute()
            # 将字典转换回 TestResult 对象
            test_result = TestResult(
                case_code=result_dict.get('case_code', ''),
                case_name=result_dict.get('case_name', ''),
                status=result_dict.get('status', 'pending'),
                duration=result_dict.get('duration', 0.0),
                error_message=result_dict.get('error_message', ''),
                metadata={k: v for k, v in result_dict.items() 
                         if k not in ['case_code', 'case_name', 'status', 'duration', 'error_message']}
            )
            self.results.append(test_result)
        
        # 断开驱动
        self.driver_manager.disconnect_all()
        
        self.end_time = datetime.now()
        
        # 使用结果构建器创建汇总
        summary = ResultBuilder.create_summary(
            product_sn=self.product_sn,
            station_id=self.station_id,
            results=self.results,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        self.status = Status(summary.status)
        return summary.to_dict()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试汇总"""
        summary = ResultBuilder.create_summary(
            product_sn=self.product_sn,
            station_id=self.station_id,
            results=self.results,
            start_time=self.start_time,
            end_time=self.end_time
        )
        return summary.to_dict()


# 向后兼容别名
TestFlow = Flow