"""
测试用例扫描器
自动扫描测试文件，提取用例元数据，同步到数据库
"""
import os
import sys
import re
import json
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import asdict

from projects.encoder_test.utils.logger import get_logger

logger = get_logger(__name__)


class CaseScanner:
    """测试用例扫描器"""
    
    def __init__(self, suites_dir: str = None, db_manager=None):
        """
        初始化扫描器
        
        Args:
            suites_dir: 测试用例目录（默认使用 core/testcases/suites）
            db_manager: 数据库管理器实例
        """
        if suites_dir is None:
            # 默认路径
            self.suites_dir = Path(__file__).parent.parent / 'testcases' / 'suites'
        else:
            self.suites_dir = Path(suites_dir)
        
        self.db_manager = db_manager
        self.scanned_cases = []
    
    def scan(self) -> List[Dict]:
        """
        扫描测试用例
        
        Returns:
            用例列表
        """
        logger.info(f"开始扫描测试用例目录: {self.suites_dir}")
        
        if not self.suites_dir.exists():
            logger.error(f"测试用例目录不存在: {self.suites_dir}")
            return []
        
        # 扫描所有 test_*.py 文件
        test_files = list(self.suites_dir.rglob('test_*.py'))
        logger.info(f"找到 {len(test_files)} 个测试文件")
        
        all_cases = []
        
        for test_file in test_files:
            cases = self._scan_file(test_file)
            all_cases.extend(cases)
        
        self.scanned_cases = all_cases
        logger.info(f"扫描完成，共发现 {len(all_cases)} 个测试用例")
        
        return all_cases
    
    def _scan_file(self, file_path: Path) -> List[Dict]:
        """
        扫描单个测试文件
        
        Args:
            file_path: 测试文件路径
            
        Returns:
            用例列表
        """
        logger.info(f"扫描文件: {file_path.name}")
        
        cases = []
        
        try:
            # 添加测试文件所在目录的父目录到 sys.path，以便正确导入依赖模块
            # 测试文件在 suites/ 目录，而 configs 在父目录 testcases/
            test_dir = str(file_path.parent.parent)
            if test_dir not in sys.path:
                sys.path.insert(0, test_dir)
            
            # 动态导入模块
            module_name = self._get_module_name(file_path)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 遍历模块中的所有类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # 只处理测试类（以 Test 开头）
                if not (isinstance(attr, type) and attr_name.startswith('Test')):
                    continue
                
                logger.info(f"  扫描测试类: {attr_name}")
                
                # 遍历类中的所有方法
                for method_name in dir(attr):
                    method = getattr(attr, method_name)
                    
                    # 只处理测试方法（以 test_ 开头）
                    if not callable(method) or not method_name.startswith('test_'):
                        continue
                    
                    # 提取用例元数据
                    case_meta = self._extract_case_meta(method, module_name, method_name)
                    if case_meta:
                        cases.append(case_meta)
        
        except Exception as e:
            logger.error(f"扫描文件 {file_path.name} 失败: {e}", exc_info=True)
        
        return cases
    
    def _get_module_name(self, file_path: Path) -> str:
        """生成模块名"""
        # 将路径转换为模块名，如 test_absolute_precision.py -> test_absolute_precision
        return file_path.stem
    
    def _extract_case_meta(self, method, module_name: str, method_name: str) -> Dict:
        """
        从测试方法中提取用例元数据
        
        优先级：
        1. @test_case 装饰器的元数据
        2. docstring 中的标记
        3. 从方法名和文件结构推断
        """
        case_meta = None
        
        # 优先级1: 检查装饰器元数据
        if hasattr(method, '_test_case_meta'):
            meta_obj = method._test_case_meta
            case_meta = {
                'case_code': meta_obj.case_code,
                'case_name': meta_obj.case_name,
                'description': meta_obj.description,
                'params': meta_obj.params,
                'category': meta_obj.category,
                'priority': meta_obj.priority,
                'enabled': meta_obj.enabled,
                'tags': meta_obj.tags,
                'module': module_name,
                'class_name': method.__qualname__.split('.')[0],
                'method_name': method_name
            }
            logger.info(f"    找到装饰器用例: {meta_obj.case_code} - {meta_obj.case_name}")
            return case_meta
        
        # 优先级2: 检查 docstring
        doc = method.__doc__ or ""
        if doc.strip():
            # 尝试从 docstring 解析元数据
            parsed = self._parse_docstring(doc, method_name)
            if parsed:
                case_meta = parsed
                logger.info(f"    从docstring解析: {case_meta['case_code']} - {case_meta['case_name']}")
                return case_meta
        
        # 优先级3: 从方法名推断
        case_meta = self._infer_from_method_name(method, module_name, method_name)
        logger.info(f"    自动推断: {case_meta['case_code']} - {case_meta['case_name']}")
        
        return case_meta
    
    def _parse_docstring(self, docstring: str, method_name: str) -> Dict:
        """
        从 docstring 解析用例元数据
        
        支持的格式:
            测试用例名称
            CaseCode: CASE-001
            Category: precision
            Params: {"angle": 45.0, "tolerance": 0.1}
        """
        lines = docstring.strip().split('\n')
        
        # 第一行作为用例名称
        case_name = lines[0].strip()
        
        # 解析元数据标记
        meta = {
            'case_code': None,
            'category': 'default',
            'params': {}
        }
        
        for line in lines[1:]:
            line = line.strip()
            
            if line.startswith('CaseCode:'):
                meta['case_code'] = line.split(':', 1)[1].strip()
            elif line.startswith('Category:'):
                meta['category'] = line.split(':', 1)[1].strip()
            elif line.startswith('Params:'):
                try:
                    meta['params'] = json.loads(line.split(':', 1)[1].strip())
                except:
                    pass
        
        if meta['case_code']:
            return {
                'case_code': meta['case_code'],
                'case_name': case_name,
                'description': docstring.strip(),
                'params': meta['params'],
                'category': meta['category'],
                'priority': 1,
                'enabled': True,
                'tags': [],
                'module': '',
                'class_name': '',
                'method_name': method_name
            }
        
        return None
    
    def _infer_from_method_name(self, method, module_name: str, method_name: str) -> Dict:
        """
        从方法名推断用例信息
        
        示例：
        - test_precision_45deg -> CASE-001 | 精度测试-45度
        - test_full_range_0_to_360 -> CASE-002 | 全范围测试0-360度
        """
        # 从模块名获取基础编号
        module_prefix = module_name.replace('test_', '')
        
        # 生成方法序号（需要在整个系统中唯一）
        # 这里使用简单哈希，实际应用中可能需要更复杂的逻辑
        method_hash = hash(f"{module_name}.{method_name}") % 10000
        
        # 生成用例编号
        case_code = f"CASE-{method_hash:04d}"
        
        # 生成用例名称（将方法名转为中文友好格式）
        case_name = self._format_method_name(method_name)
        
        # 从 docstring 获取描述
        description = method.__doc__ or ""
        
        # 尝试从配置文件获取参数（如果存在）
        params = self._try_load_params(module_name, method_name)
        
        return {
            'case_code': case_code,
            'case_name': case_name,
            'description': description.strip(),
            'params': params,
            'category': module_prefix,
            'priority': 1,
            'enabled': True,
            'tags': [module_prefix],
            'module': module_name,
            'class_name': method.__qualname__.split('.')[0],
            'method_name': method_name
        }
    
    def _format_method_name(self, method_name: str) -> str:
        """将方法名转为友好的显示名称"""
        # 移除 test_ 前缀
        name = method_name.replace('test_', '')
        
        # 将下划线转为空格，首字母大写
        words = name.split('_')
        formatted = ' '.join(w.capitalize() for w in words)
        
        # 添加数字单位的中文转换
        formatted = formatted.replace('Deg', '度')
        formatted = formatted.replace('To', '到')
        
        return formatted
    
    def _try_load_params(self, module_name: str, method_name: str) -> Dict:
        """
        尝试从配置文件加载测试参数
        
        配置文件路径: core/testcases/configs/{module_name}_config.py
        """
        try:
            # 尝试加载配置模块
            config_module_name = f'core.testcases.configs.{module_name}_config'
            config_module = importlib.import_module(config_module_name)
            
            # 查找配置类
            for attr_name in dir(config_module):
                if attr_name.endswith('Config') and attr_name != 'BaseConfig':
                    config_class = getattr(config_module, attr_name)
                    if hasattr(config_class, 'to_dict'):
                        return config_class().to_dict()
                    elif hasattr(config_class, '__dict__'):
                        # 提取所有非私有属性
                        return {k: v for k, v in vars(config_class).items() 
                                if not k.startswith('_') and not callable(v)}
        
        except Exception as e:
            logger.debug(f"加载配置失败 {module_name}: {e}")
        
        return {}
    
    def sync_to_database(self, cases: List[Dict] = None) -> Dict:
        """
        同步用例到数据库
        
        Args:
            cases: 用例列表（如果不提供则使用上次扫描的结果）
            
        Returns:
            同步结果统计
        """
        if not self.db_manager:
            logger.error("数据库管理器未配置，无法同步")
            return {'success': False, 'error': '数据库管理器未配置'}
        
        if cases is None:
            cases = self.scanned_cases
        
        if not cases:
            logger.warning("没有用例需要同步")
            return {'success': True, 'added': 0, 'updated': 0, 'disabled': 0}
        
        stats = {'added': 0, 'updated': 0, 'disabled': 0}
        
        try:
            # 获取数据库中现有的用例
            existing_sql = "SELECT case_code, id FROM test_case WHERE is_deleted = 0"
            existing_records = self.db_manager.query(existing_sql)
            existing_codes = {row[0]: row[1] for row in existing_records}
            
            logger.info(f"数据库中有 {len(existing_codes)} 个现有用例")
            
            # 同步每个用例
            for case in cases:
                case_code = case['case_code']
                
                # 将参数转为JSON字符串
                params_json = json.dumps(case.get('params', {}), ensure_ascii=False)
                
                if case_code in existing_codes:
                    # 更新现有用例
                    case_id = existing_codes[case_code]
                    update_sql = """
                        UPDATE test_case 
                        SET case_name = %s, 
                            params = %s, 
                            description = %s,
                            category = %s,
                            priority = %s,
                            tags = %s,
                            module_path = %s,
                            class_name = %s,
                            method_name = %s,
                            status = 1,
                            update_time = NOW()
                        WHERE id = %s
                    """
                    self.db_manager.execute(update_sql, (
                        case['case_name'],
                        params_json,
                        case.get('description', ''),
                        case.get('category', 'default'),
                        case.get('priority', 1),
                        json.dumps(case.get('tags', []), ensure_ascii=False),
                        case.get('module', ''),
                        case.get('class_name', ''),
                        case.get('method_name', ''),
                        case_id
                    ), fetch=False)
                    stats['updated'] += 1
                    logger.debug(f"更新用例: {case_code}")
                else:
                    # 插入新用例
                    insert_sql = """
                        INSERT INTO test_case 
                        (case_code, case_name, params, description, category, priority, tags, 
                         module_path, class_name, method_name, status, create_time, update_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
                    """
                    self.db_manager.execute(insert_sql, (
                        case_code,
                        case['case_name'],
                        params_json,
                        case.get('description', ''),
                        case.get('category', 'default'),
                        case.get('priority', 1),
                        json.dumps(case.get('tags', []), ensure_ascii=False),
                        case.get('module', ''),
                        case.get('class_name', ''),
                        case.get('method_name', '')
                    ), fetch=False)
                    stats['added'] += 1
                    logger.debug(f"添加用例: {case_code}")
            
            # 禁用数据库中已删除的用例（代码中不存在但数据库中存在的）
            scanned_codes = {case['case_code'] for case in cases}
            codes_to_disable = set(existing_codes.keys()) - scanned_codes
            
            if codes_to_disable:
                disable_sql = """
                    UPDATE test_case 
                    SET status = 0, update_time = NOW()
                    WHERE case_code IN ({})
                """.format(','.join(['%s'] * len(codes_to_disable)))
                
                self.db_manager.execute(disable_sql, list(codes_to_disable), fetch=False)
                stats['disabled'] = len(codes_to_disable)
                logger.info(f"禁用已删除的用例: {codes_to_disable}")
            
            logger.info(f"同步完成: 新增={stats['added']}, 更新={stats['updated']}, 禁用={stats['disabled']}")
            
            return {'success': True, **stats}
        
        except Exception as e:
            logger.error(f"同步到数据库失败: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}


def sync_test_cases(db_manager=None, suites_dir=None) -> Dict:
    """
    便捷函数：扫描并同步测试用例
    
    Args:
        db_manager: 数据库管理器
        suites_dir: 测试用例目录
        
    Returns:
        同步结果
    """
    scanner = CaseScanner(suites_dir=suites_dir, db_manager=db_manager)
    cases = scanner.scan()
    return scanner.sync_to_database(cases)