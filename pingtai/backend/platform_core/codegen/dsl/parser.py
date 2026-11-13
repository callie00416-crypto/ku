"""
领域特定语言 - Domain Specific Language

【职责】
- 定义代码生成的DSL语法
- 解析DSL描述
- 提供DSL验证
"""
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import re


class DSLTokenType(Enum):
    """DSL词法单元类型"""
    KEYWORD = "keyword"
    IDENTIFIER = "identifier"
    STRING = "string"
    NUMBER = "number"
    OPERATOR = "operator"
    PUNCTUATION = "punctuation"
    COMMENT = "comment"
    WHITESPACE = "whitespace"


@dataclass
class DSLToken:
    """DSL词法单元"""
    type: DSLTokenType
    value: str
    line: int
    column: int


class DSLLexer:
    """DSL词法分析器"""
    
    KEYWORDS = {
        'device', 'module', 'function', 'class', 'interface',
        'property', 'method', 'parameter', 'return', 'import',
        'extends', 'implements', 'abstract', 'static', 'final',
        'public', 'private', 'protected', 'async', 'await'
    }
    
    OPERATORS = {
        '=', '+', '-', '*', '/', '%', '**', '//',
        '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!',
        '&', '|', '^', '~', '<<', '>>', '+=', '-=', '*=', '/='
    }
    
    PUNCTUATIONS = {
        '(', ')', '[', ']', '{', '}', ',', ':', ';', '.', '...'
    }
    
    def __init__(self):
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
    
    def tokenize(self, source: str) -> List[DSLToken]:
        """词法分析
        
        Args:
            source: DSL源代码
            
        Returns:
            词法单元列表
        """
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
        
        i = 0
        while i < len(source):
            char = source[i]
            
            # 跳过空白字符
            if char.isspace():
                if char == '\n':
                    self.current_line += 1
                    self.current_column = 1
                else:
                    self.current_column += 1
                i += 1
                continue
            
            # 注释
            if char == '#' and (i == 0 or source[i-1] in '\n '):
                comment_end = source.find('\n', i)
                if comment_end == -1:
                    comment_end = len(source)
                comment = source[i:comment_end]
                self.tokens.append(DSLToken(
                    DSLTokenType.COMMENT, comment, self.current_line, self.current_column
                ))
                i = comment_end
                continue
            
            # 字符串
            if char in '"\'':
                string_end = source.find(char, i + 1)
                if string_end == -1:
                    raise ValueError(f"未闭合的字符串 at line {self.current_line}")
                string_value = source[i+1:string_end]
                self.tokens.append(DSLToken(
                    DSLTokenType.STRING, string_value, self.current_line, self.current_column
                ))
                self.current_column += (string_end - i + 1)
                i = string_end + 1
                continue
            
            # 数字
            if char.isdigit():
                num_end = i
                while num_end < len(source) and (source[num_end].isdigit() or source[num_end] == '.'):
                    num_end += 1
                number = source[i:num_end]
                self.tokens.append(DSLToken(
                    DSLTokenType.NUMBER, number, self.current_line, self.current_column
                ))
                self.current_column += (num_end - i)
                i = num_end
                continue
            
            # 标识符和关键字
            if char.isalpha() or char == '_':
                ident_end = i
                while ident_end < len(source) and (source[ident_end].isalnum() or source[ident_end] == '_'):
                    ident_end += 1
                identifier = source[i:ident_end]
                
                if identifier in self.KEYWORDS:
                    token_type = DSLTokenType.KEYWORD
                else:
                    token_type = DSLTokenType.IDENTIFIER
                
                self.tokens.append(DSLToken(
                    token_type, identifier, self.current_line, self.current_column
                ))
                self.current_column += (ident_end - i)
                i = ident_end
                continue
            
            # 操作符
            if char in self.OPERATORS:
                # 检查双字符操作符
                if i + 1 < len(source) and source[i:i+2] in self.OPERATORS:
                    op = source[i:i+2]
                    self.tokens.append(DSLToken(
                        DSLTokenType.OPERATOR, op, self.current_line, self.current_column
                    ))
                    self.current_column += 2
                    i += 2
                else:
                    self.tokens.append(DSLToken(
                        DSLTokenType.OPERATOR, char, self.current_line, self.current_column
                    ))
                    self.current_column += 1
                    i += 1
                continue
            
            # 标点符号
            if char in self.PUNCTUATIONS:
                self.tokens.append(DSLToken(
                    DSLTokenType.PUNCTUATION, char, self.current_line, self.current_column
                ))
                self.current_column += 1
                i += 1
                continue
            
            # 未知字符
            raise ValueError(f"未知字符: {char} at line {self.current_line}, column {self.current_column}")
        
        return self.tokens


class DSLParser:
    """DSL语法分析器"""
    
    def __init__(self, tokens: List[DSLToken]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Dict[str, Any]:
        """语法分析
        
        Returns:
            AST字典
        """
        return self.parse_program()
    
    def parse_program(self) -> Dict[str, Any]:
        """解析程序"""
        statements = []
        
        while not self.is_at_end():
            statements.append(self.parse_statement())
        
        return {
            'type': 'Program',
            'body': statements
        }
    
    def parse_statement(self) -> Dict[str, Any]:
        """解析语句"""
        if self.match_keyword('device'):
            return self.parse_device_declaration()
        elif self.match_keyword('module'):
            return self.parse_module_declaration()
        elif self.match_keyword('class'):
            return self.parse_class_declaration()
        elif self.match_keyword('function'):
            return self.parse_function_declaration()
        else:
            return self.parse_expression_statement()
    
    def parse_device_declaration(self) -> Dict[str, Any]:
        """解析设备声明"""
        name = self.consume_identifier()
        
        properties = {}
        methods = {}
        
        self.consume_punctuation('{')
        
        while not self.check_punctuation('}') and not self.is_at_end():
            if self.match_keyword('property'):
                prop_name = self.consume_identifier()
                self.consume_operator('=')
                prop_value = self.parse_expression()
                self.consume_punctuation(';')
                properties[prop_name] = prop_value
            elif self.match_keyword('method'):
                method_name = self.consume_identifier()
                self.consume_punctuation('(')
                params = self.parse_parameters()
                self.consume_punctuation(')')
                method_body = self.parse_block()
                methods[method_name] = {
                    'parameters': params,
                    'body': method_body
                }
        
        self.consume_punctuation('}')
        
        return {
            'type': 'DeviceDeclaration',
            'name': name,
            'properties': properties,
            'methods': methods
        }
    
    def parse_module_declaration(self) -> Dict[str, Any]:
        """解析模块声明"""
        name = self.consume_identifier()
        
        imports = []
        classes = []
        functions = []
        
        self.consume_punctuation('{')
        
        while not self.check_punctuation('}') and not self.is_at_end():
            if self.match_keyword('import'):
                import_name = self.consume_identifier()
                imports.append(import_name)
                self.consume_punctuation(';')
            elif self.match_keyword('class'):
                classes.append(self.parse_class_declaration())
            elif self.match_keyword('function'):
                functions.append(self.parse_function_declaration())
        
        self.consume_punctuation('}')
        
        return {
            'type': 'ModuleDeclaration',
            'name': name,
            'imports': imports,
            'classes': classes,
            'functions': functions
        }
    
    def parse_class_declaration(self) -> Dict[str, Any]:
        """解析类声明"""
        name = self.consume_identifier()
        
        extends = None
        if self.match_keyword('extends'):
            extends = self.consume_identifier()
        
        properties = {}
        methods = {}
        
        self.consume_punctuation('{')
        
        while not self.check_punctuation('}') and not self.is_at_end():
            if self.match_keyword('property'):
                prop_name = self.consume_identifier()
                self.consume_operator('=')
                prop_value = self.parse_expression()
                self.consume_punctuation(';')
                properties[prop_name] = prop_value
            elif self.match_keyword('method'):
                method_name = self.consume_identifier()
                self.consume_punctuation('(')
                params = self.parse_parameters()
                self.consume_punctuation(')')
                method_body = self.parse_block()
                methods[method_name] = {
                    'parameters': params,
                    'body': method_body
                }
        
        self.consume_punctuation('}')
        
        return {
            'type': 'ClassDeclaration',
            'name': name,
            'extends': extends,
            'properties': properties,
            'methods': methods
        }
    
    def parse_function_declaration(self) -> Dict[str, Any]:
        """解析函数声明"""
        name = self.consume_identifier()
        self.consume_punctuation('(')
        params = self.parse_parameters()
        self.consume_punctuation(')')
        body = self.parse_block()
        
        return {
            'type': 'FunctionDeclaration',
            'name': name,
            'parameters': params,
            'body': body
        }
    
    def parse_parameters(self) -> List[str]:
        """解析参数列表"""
        params = []
        
        if not self.check_punctuation(')'):
            params.append(self.consume_identifier())
            while self.match_punctuation(','):
                params.append(self.consume_identifier())
        
        return params
    
    def parse_block(self) -> List[Dict[str, Any]]:
        """解析代码块"""
        statements = []
        
        self.consume_punctuation('{')
        
        while not self.check_punctuation('}') and not self.is_at_end():
            statements.append(self.parse_statement())
        
        self.consume_punctuation('}')
        
        return statements
    
    def parse_expression_statement(self) -> Dict[str, Any]:
        """解析表达式语句"""
        expr = self.parse_expression()
        self.consume_punctuation(';')
        
        return {
            'type': 'ExpressionStatement',
            'expression': expr
        }
    
    def parse_expression(self) -> Dict[str, Any]:
        """解析表达式"""
        return self.parse_assignment()
    
    def parse_assignment(self) -> Dict[str, Any]:
        """解析赋值表达式"""
        expr = self.parse_equality()
        
        if self.match_operator('='):
            value = self.parse_assignment()
            return {
                'type': 'AssignmentExpression',
                'left': expr,
                'right': value
            }
        
        return expr
    
    def parse_equality(self) -> Dict[str, Any]:
        """解析相等性表达式"""
        expr = self.parse_comparison()
        
        while self.match_operator('==') or self.match_operator('!='):
            operator = self.tokens[self.current - 1].value
            right = self.parse_comparison()
            expr = {
                'type': 'BinaryExpression',
                'operator': operator,
                'left': expr,
                'right': right
            }
        
        return expr
    
    def parse_comparison(self) -> Dict[str, Any]:
        """解析比较表达式"""
        expr = self.parse_term()
        
        while self.match_operator('<') or self.match_operator('>') or \
              self.match_operator('<=') or self.match_operator('>='):
            operator = self.tokens[self.current - 1].value
            right = self.parse_term()
            expr = {
                'type': 'BinaryExpression',
                'operator': operator,
                'left': expr,
                'right': right
            }
        
        return expr
    
    def parse_term(self) -> Dict[str, Any]:
        """解析项表达式"""
        expr = self.parse_factor()
        
        while self.match_operator('+') or self.match_operator('-'):
            operator = self.tokens[self.current - 1].value
            right = self.parse_factor()
            expr = {
                'type': 'BinaryExpression',
                'operator': operator,
                'left': expr,
                'right': right
            }
        
        return expr
    
    def parse_factor(self) -> Dict[str, Any]:
        """解析因子表达式"""
        expr = self.parse_unary()
        
        while self.match_operator('*') or self.match_operator('/') or self.match_operator('%'):
            operator = self.tokens[self.current - 1].value
            right = self.parse_unary()
            expr = {
                'type': 'BinaryExpression',
                'operator': operator,
                'left': expr,
                'right': right
            }
        
        return expr
    
    def parse_unary(self) -> Dict[str, Any]:
        """解析一元表达式"""
        if self.match_operator('!') or self.match_operator('-'):
            operator = self.tokens[self.current - 1].value
            right = self.parse_unary()
            return {
                'type': 'UnaryExpression',
                'operator': operator,
                'right': right
            }
        
        return self.parse_primary()
    
    def parse_primary(self) -> Dict[str, Any]:
        """解析基本表达式"""
        if self.match_punctuation('('):
            expr = self.parse_expression()
            self.consume_punctuation(')')
            return expr
        
        token = self.advance()
        
        if token.type == DSLTokenType.IDENTIFIER:
            return {
                'type': 'Identifier',
                'name': token.value
            }
        elif token.type == DSLTokenType.NUMBER:
            return {
                'type': 'NumberLiteral',
                'value': float(token.value) if '.' in token.value else int(token.value)
            }
        elif token.type == DSLTokenType.STRING:
            return {
                'type': 'StringLiteral',
                'value': token.value
            }
        
        raise ValueError(f"意外的token: {token.type} {token.value}")
    
    # 辅助方法
    def is_at_end(self) -> bool:
        """是否到达结尾"""
        return self.current >= len(self.tokens)
    
    def advance(self) -> DSLToken:
        """前进一个token"""
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]
    
    def peek(self) -> DSLToken:
        """查看当前token"""
        if self.is_at_end():
            raise ValueError("意外的文件结束")
        return self.tokens[self.current]
    
    def check_keyword(self, keyword: str) -> bool:
        """检查是否为指定关键字"""
        if self.is_at_end():
            return False
        token = self.peek()
        return token.type == DSLTokenType.KEYWORD and token.value == keyword
    
    def match_keyword(self, keyword: str) -> bool:
        """匹配并消耗关键字"""
        if self.check_keyword(keyword):
            self.advance()
            return True
        return False
    
    def check_operator(self, operator: str) -> bool:
        """检查是否为指定操作符"""
        if self.is_at_end():
            return False
        token = self.peek()
        return token.type == DSLTokenType.OPERATOR and token.value == operator
    
    def match_operator(self, operator: str) -> bool:
        """匹配并消耗操作符"""
        if self.check_operator(operator):
            self.advance()
            return True
        return False
    
    def check_punctuation(self, punct: str) -> bool:
        """检查是否为指定标点"""
        if self.is_at_end():
            return False
        token = self.peek()
        return token.type == DSLTokenType.PUNCTUATION and token.value == punct
    
    def match_punctuation(self, punct: str) -> bool:
        """匹配并消耗标点"""
        if self.check_punctuation(punct):
            self.advance()
            return True
        return False
    
    def consume_identifier(self) -> str:
        """消耗标识符"""
        token = self.advance()
        if token.type != DSLTokenType.IDENTIFIER:
            raise ValueError(f"期望标识符，得到: {token.type}")
        return token.value
    
    def consume_operator(self, operator: str) -> str:
        """消耗操作符"""
        token = self.advance()
        if token.type != DSLTokenType.OPERATOR or token.value != operator:
            raise ValueError(f"期望操作符 '{operator}'，得到: {token.value}")
        return operator
    
    def consume_punctuation(self, punct: str) -> str:
        """消耗标点"""
        token = self.advance()
        if token.type != DSLTokenType.PUNCTUATION or token.value != punct:
            raise ValueError(f"期望标点 '{punct}'，得到: {token.value}")
        return punct


class DSLValidator:
    """DSL验证器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, ast: Dict[str, Any]) -> bool:
        """验证AST
        
        Args:
            ast: 抽象语法树
            
        Returns:
            是否有效
        """
        self.errors = []
        self.warnings = []
        
        self.validate_node(ast)
        
        return len(self.errors) == 0
    
    def validate_node(self, node: Dict[str, Any]):
        """验证节点"""
        node_type = node.get('type')
        
        if node_type == 'Program':
            self.validate_program(node)
        elif node_type == 'DeviceDeclaration':
            self.validate_device_declaration(node)
        elif node_type == 'ClassDeclaration':
            self.validate_class_declaration(node)
        elif node_type == 'FunctionDeclaration':
            self.validate_function_declaration(node)
    
    def validate_program(self, node: Dict[str, Any]):
        """验证程序"""
        body = node.get('body', [])
        
        for statement in body:
            self.validate_node(statement)
    
    def validate_device_declaration(self, node: Dict[str, Any]):
        """验证设备声明"""
        name = node.get('name')
        if not name:
            self.errors.append("设备声明缺少名称")
        
        properties = node.get('properties', {})
        for prop_name, prop_value in properties.items():
            if not isinstance(prop_name, str):
                self.errors.append(f"属性名称必须是字符串: {prop_name}")
    
    def validate_class_declaration(self, node: Dict[str, Any]):
        """验证类声明"""
        name = node.get('name')
        if not name:
            self.errors.append("类声明缺少名称")
        
        # 检查方法名重复
        methods = node.get('methods', {})
        method_names = list(methods.keys())
        if len(method_names) != len(set(method_names)):
            self.errors.append("类中存在重复的方法名")
    
    def validate_function_declaration(self, node: Dict[str, Any]):
        """验证函数声明"""
        name = node.get('name')
        if not name:
            self.errors.append("函数声明缺少名称")
        
        # 检查参数名重复
        parameters = node.get('parameters', [])
        if len(parameters) != len(set(parameters)):
            self.errors.append(f"函数 {name} 中存在重复的参数名")


class DSLCompiler:
    """DSL编译器"""
    
    def __init__(self):
        self.lexer = DSLLexer()
        self.validator = DSLValidator()
    
    def compile(self, source: str) -> Dict[str, Any]:
        """编译DSL源代码
        
        Args:
            source: DSL源代码
            
        Returns:
            编译结果
        """
        try:
            # 词法分析
            tokens = self.lexer.tokenize(source)
            
            # 语法分析
            parser = DSLParser(tokens)
            ast = parser.parse()
            
            # 语义验证
            if not self.validator.validate(ast):
                return {
                    'success': False,
                    'errors': self.validator.errors,
                    'warnings': self.validator.warnings
                }
            
            return {
                'success': True,
                'ast': ast,
                'warnings': self.validator.warnings
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'warnings': []
            }