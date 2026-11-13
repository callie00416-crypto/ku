"""
AST处理器 - AST Processor

【职责】
- 代码语法分析
- AST转换和优化
- 代码验证和检查
"""
from typing import Dict, Any, List, Optional
import logging
import ast


logger = logging.getLogger(__name__)


class ASTProcessor:
    """AST处理器
    
    【职责】
- 解析代码为AST
- 验证代码语法
- 优化代码结构
- 代码分析和转换
    """
    
    def __init__(self, config):
        """
        Args:
            config: 平台配置
        """
        self.config = config
        self.language = config.ast.language
        self.validate_syntax = config.ast.validate_syntax
        self.optimize_ast = config.ast.optimize_ast
        
        logger.info(f"AST处理器初始化完成，语言: {self.language}")
    
    def parse(self, code: str) -> ast.AST:
        """解析代码为AST
        
        Args:
            code: 源代码
            
        Returns:
            AST对象
        """
        try:
            tree = ast.parse(code)
            logger.debug("代码解析成功")
            return tree
        except SyntaxError as e:
            logger.error(f"代码解析失败: {e}")
            raise
    
    def validate(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """验证代码
        
        Args:
            code: 源代码
            language: 编程语言
            
        Returns:
            验证结果
        """
        try:
            if language != 'python':
                return {
                    'valid': True,
                    'message': f'语言 {language} 暂不支持验证',
                    'warnings': []
                }
            
            # 解析代码
            tree = self.parse(code)
            
            # 执行验证
            validator = CodeValidator()
            validator.visit(tree)
            
            return {
                'valid': len(validator.errors) == 0,
                'errors': validator.errors,
                'warnings': validator.warnings,
                'message': '代码验证完成'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [str(e)],
                'warnings': [],
                'message': '代码验证失败'
            }
    
    def optimize(self, code: str, language: str = 'python') -> str:
        """优化代码
        
        Args:
            code: 源代码
            language: 编程语言
            
        Returns:
            优化后的代码
        """
        try:
            if language != 'python':
                return code
            
            # 解析代码
            tree = self.parse(code)
            
            # 执行优化
            if self.optimize_ast:
                optimizer = ASTOptimizer()
                tree = optimizer.visit(tree)
                ast.fix_missing_locations(tree)
            
            # 生成代码
            optimized_code = ast.unparse(tree)
            
            logger.debug("代码优化完成")
            return optimized_code
            
        except Exception as e:
            logger.warning(f"代码优化失败: {e}")
            return code
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """分析代码
        
        Args:
            code: 源代码
            
        Returns:
            分析结果
        """
        try:
            tree = self.parse(code)
            analyzer = CodeAnalyzer()
            analyzer.visit(tree)
            
            return {
                'functions': analyzer.functions,
                'classes': analyzer.classes,
                'imports': analyzer.imports,
                'complexity': analyzer.complexity,
                'lines_of_code': len(code.splitlines()),
                'docstrings': analyzer.docstrings
            }
            
        except Exception as e:
            logger.error(f"代码分析失败: {e}")
            return {
                'error': str(e)
            }
    
    def transform(self, code: str, transformations: List[Dict[str, Any]]) -> str:
        """转换代码
        
        Args:
            code: 源代码
            transformations: 转换规则列表
            
        Returns:
            转换后的代码
        """
        try:
            tree = self.parse(code)
            
            # 应用转换
            transformer = CodeTransformer(transformations)
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)
            
            # 生成代码
            transformed_code = ast.unparse(tree)
            
            logger.debug(f"代码转换完成，应用了 {len(transformations)} 个转换")
            return transformed_code
            
        except Exception as e:
            logger.error(f"代码转换失败: {e}")
            return code


class CodeValidator(ast.NodeVisitor):
    """代码验证器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.current_function = None
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        """验证函数定义"""
        # 检查函数文档字符串
        if not ast.get_docstring(node):
            self.warnings.append({
                'type': 'missing_docstring',
                'message': f"函数 '{node.name}' 缺少文档字符串",
                'line': node.lineno
            })
        
        # 检查函数参数
        if len(node.args.args) > 7:
            self.warnings.append({
                'type': 'too_many_parameters',
                'message': f"函数 '{node.name}' 参数过多 ({len(node.args.args)} 个)",
                'line': node.lineno
            })
        
        # 检查函数复杂度
        complexity = self._calculate_complexity(node)
        if complexity > 10:
            self.warnings.append({
                'type': 'high_complexity',
                'message': f"函数 '{node.name}' 复杂度过高 ({complexity})",
                'line': node.lineno
            })
        
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = None
    
    def visit_ClassDef(self, node):
        """验证类定义"""
        # 检查类文档字符串
        if not ast.get_docstring(node):
            self.warnings.append({
                'type': 'missing_docstring',
                'message': f"类 '{node.name}' 缺少文档字符串",
                'line': node.lineno
            })
        
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None
    
    def visit_Import(self, node):
        """验证导入语句"""
        for alias in node.names:
            if alias.name.startswith('.'):
                if len(alias.name.split('.')) > 3:
                    self.warnings.append({
                        'type': 'deep_relative_import',
                        'message': f"深层相对导入: {alias.name}",
                        'line': node.lineno
                    })
    
    def _calculate_complexity(self, node) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


class ASTOptimizer(ast.NodeTransformer):
    """AST优化器"""
    
    def visit_Constant(self, node):
        """优化常量"""
        # 常量折叠
        if isinstance(node.value, (int, float, str, bool)):
            return node
        return self.generic_visit(node)
    
    def visit_BinOp(self, node):
        """优化二元操作"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # 常量折叠
        if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
            try:
                if isinstance(node.op, ast.Add):
                    result = left.value + right.value
                elif isinstance(node.op, ast.Sub):
                    result = left.value - right.value
                elif isinstance(node.op, ast.Mult):
                    result = left.value * right.value
                elif isinstance(node.op, ast.Div):
                    result = left.value / right.value
                else:
                    return ast.BinOp(left, node.op, right)
                
                return ast.Constant(value=result)
            except:
                pass
        
        return ast.BinOp(left, node.op, right)
    
    def visit_Compare(self, node):
        """优化比较操作"""
        left = self.visit(node.left)
        comparators = [self.visit(comp) for comp in node.comparators]
        
        # 简化比较
        if isinstance(left, ast.Constant) and all(isinstance(comp, ast.Constant) for comp in comparators):
            try:
                if len(node.ops) == 1:
                    op = node.ops[0]
                    comp = comparators[0]
                    
                    if isinstance(op, ast.Eq):
                        result = left.value == comp.value
                    elif isinstance(op, ast.NotEq):
                        result = left.value != comp.value
                    elif isinstance(op, ast.Lt):
                        result = left.value < comp.value
                    elif isinstance(op, ast.LtE):
                        result = left.value <= comp.value
                    elif isinstance(op, ast.Gt):
                        result = left.value > comp.value
                    elif isinstance(op, ast.GtE):
                        result = left.value >= comp.value
                    else:
                        return ast.Compare(left, node.ops, comparators)
                    
                    return ast.Constant(value=result)
            except:
                pass
        
        return ast.Compare(left, node.ops, comparators)


class CodeAnalyzer(ast.NodeVisitor):
    """代码分析器"""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.complexity = 0
        self.docstrings = []
    
    def visit_FunctionDef(self, node):
        """分析函数"""
        docstring = ast.get_docstring(node)
        complexity = self._calculate_complexity(node)
        
        self.functions.append({
            'name': node.name,
            'lineno': node.lineno,
            'args': [arg.arg for arg in node.args.args],
            'docstring': docstring,
            'complexity': complexity
        })
        
        if docstring:
            self.docstrings.append({
                'type': 'function',
                'name': node.name,
                'docstring': docstring
            })
        
        self.complexity += complexity
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """分析类"""
        docstring = ast.get_docstring(node)
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        
        self.classes.append({
            'name': node.name,
            'lineno': node.lineno,
            'bases': [ast.unparse(base) for base in node.bases],
            'methods': methods,
            'docstring': docstring
        })
        
        if docstring:
            self.docstrings.append({
                'type': 'class',
                'name': node.name,
                'docstring': docstring
            })
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """分析导入"""
        for alias in node.names:
            self.imports.append({
                'module': alias.name,
                'alias': alias.asname,
                'lineno': node.lineno
            })
    
    def visit_ImportFrom(self, node):
        """分析from导入"""
        module = node.module if node.module else ''
        for alias in node.names:
            self.imports.append({
                'module': module,
                'name': alias.name,
                'alias': alias.asname,
                'lineno': node.lineno
            })
    
    def _calculate_complexity(self, node) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


class CodeTransformer(ast.NodeTransformer):
    """代码转换器"""
    
    def __init__(self, transformations: List[Dict[str, Any]]):
        """
        Args:
            transformations: 转换规则列表
        """
        self.transformations = transformations
    
    def visit_FunctionDef(self, node):
        """转换函数定义"""
        # 应用转换规则
        for transform in self.transformations:
            if transform.get('type') == 'rename_function':
                if node.name == transform.get('from_name'):
                    node.name = transform.get('to_name', node.name)
        
        self.generic_visit(node)
        return node
    
    def visit_ClassDef(self, node):
        """转换类定义"""
        # 应用转换规则
        for transform in self.transformations:
            if transform.get('type') == 'rename_class':
                if node.name == transform.get('from_name'):
                    node.name = transform.get('to_name', node.name)
        
        self.generic_visit(node)
        return node
    
    def visit_Name(self, node):
        """转换名称引用"""
        # 应用转换规则
        for transform in self.transformations:
            if transform.get('type') == 'rename_variable':
                if node.id == transform.get('from_name'):
                    node.id = transform.get('to_name', node.id)
        
        return node