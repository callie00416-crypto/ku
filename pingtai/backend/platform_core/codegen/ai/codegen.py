"""
AI代码生成器 - AI Code Generator

【职责】
- 集成AI模型生成代码
- 提示词工程
- 代码优化和补全
"""
from typing import Dict, Any, Optional, List
import logging
import json


logger = logging.getLogger(__name__)


class AICodeGenerator:
    """AI代码生成器
    
    【职责】
- 调用AI模型生成代码
- 提示词优化
- 代码质量检查
    """
    
    def __init__(self, config):
        """
        Args:
            config: 平台配置
        """
        self.config = config
        self.enabled = config.ai.enabled
        self.model = config.ai.model
        self.api_key = config.ai.api_key
        self.max_tokens = config.ai.max_tokens
        self.temperature = config.ai.temperature
        
        # 生成统计
        self.stats = {
            'requests_made': 0,
            'tokens_used': 0,
            'errors': 0
        }
        
        logger.info(f"AI代码生成器初始化完成，模型: {self.model}")
    
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """生成代码
        
        Args:
            prompt: 提示词
            context: 上下文信息
            
        Returns:
            生成的代码
        """
        if not self.enabled:
            raise RuntimeError("AI代码生成功能未启用")
        
        try:
            # 构建完整提示词
            full_prompt = self._build_prompt(prompt, context)
            
            # 调用AI模型
            response = self._call_ai_model(full_prompt)
            
            # 提取代码
            code = self._extract_code(response)
            
            # 更新统计
            self.stats['requests_made'] += 1
            self.stats['tokens_used'] += len(full_prompt) + len(response)
            
            logger.info(f"AI代码生成完成，长度: {len(code)} 字符")
            return code
            
        except Exception as e:
            logger.error(f"AI代码生成失败: {e}")
            self.stats['errors'] += 1
            raise
    
    def generate_device(self, device_spec: Dict[str, Any]) -> str:
        """生成设备驱动代码
        
        Args:
            device_spec: 设备规范
            
        Returns:
            生成的设备代码
        """
        prompt = self._build_device_prompt(device_spec)
        return self.generate(prompt, {'spec': device_spec})
    
    def generate_class(self, class_spec: Dict[str, Any]) -> str:
        """生成类代码
        
        Args:
            class_spec: 类规范
            
        Returns:
            生成的类代码
        """
        prompt = self._build_class_prompt(class_spec)
        return self.generate(prompt, {'spec': class_spec})
    
    def generate_function(self, function_spec: Dict[str, Any]) -> str:
        """生成函数代码
        
        Args:
            function_spec: 函数规范
            
        Returns:
            生成的函数代码
        """
        prompt = self._build_function_prompt(function_spec)
        return self.generate(prompt, {'spec': function_spec})
    
    def optimize_code(self, code: str, optimization_type: str = 'performance') -> str:
        """优化代码
        
        Args:
            code: 原始代码
            optimization_type: 优化类型 (performance, readability, security)
            
        Returns:
            优化后的代码
        """
        prompt = self._build_optimization_prompt(code, optimization_type)
        return self.generate(prompt, {'code': code, 'type': optimization_type})
    
    def complete_code(self, partial_code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """补全代码
        
        Args:
            partial_code: 部分代码
            context: 上下文信息
            
        Returns:
            补全后的代码
        """
        prompt = self._build_completion_prompt(partial_code, context)
        return self.generate(prompt, {'code': partial_code, **(context or {})})
    
    def _build_prompt(self, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """构建完整提示词
        
        Args:
            user_prompt: 用户提示词
            context: 上下文信息
            
        Returns:
            完整提示词
        """
        system_prompt = """你是一个专业的工业自动化软件工程师，擅长编写Python代码。

【代码规范】
1. 遵循PEP 8代码风格
2. 使用类型提示
3. 编写完整的文档字符串
4. 实现适当的错误处理
5. 添加必要的日志记录

【架构要求】
1. 遵循平台/项目/共享分层架构
2. 使用依赖注入模式
3. 实现清晰的接口设计
4. 支持单元测试

【工业特性】
1. 考虑异常恢复机制
2. 实现健康检查
3. 支持设备生命周期管理
4. 提供详细的错误信息

请根据以上规范生成高质量的代码。"""

        if context:
            context_info = f"\n【上下文信息】\n{json.dumps(context, indent=2, ensure_ascii=False)}"
        else:
            context_info = ""

        full_prompt = f"{system_prompt}{context_info}\n\n【用户请求】\n{user_prompt}\n\n【生成的代码】"
        
        return full_prompt
    
    def _build_device_prompt(self, device_spec: Dict[str, Any]) -> str:
        """构建设备生成提示词"""
        return f"""请生成一个工业设备驱动类，要求如下：

【设备信息】
- 设备名称: {device_spec.get('name', 'new_device')}
- 制造商: {device_spec.get('manufacturer', 'Unknown')}
- 型号: {device_spec.get('model', 'Unknown')}
- 通信协议: {device_spec.get('protocol', 'unknown')}
- 通信方式: {device_spec.get('communication', 'unknown')}
- 描述: {device_spec.get('description', '')}

【技术要求】
1. 继承BaseDevice基类
2. 实现connect/disconnect方法
3. 实现read_data/write_data方法
4. 实现health_check方法
5. 集成平台设备生命周期管理
6. 完整的错误处理和日志记录

【设备参数】
{json.dumps(device_spec.get('parameters', {}), indent=2, ensure_ascii=False)}

【设备方法】
{json.dumps(device_spec.get('methods', []), indent=2, ensure_ascii=False)}

请生成完整的设备驱动代码。"""
    
    def _build_class_prompt(self, class_spec: Dict[str, Any]) -> str:
        """构建类生成提示词"""
        return f"""请生成一个Python类，要求如下：

【类信息】
- 类名: {class_spec.get('name', 'NewClass')}
- 描述: {class_spec.get('description', '')}
- 基类: {class_spec.get('base_class', 'object')}

【类属性】
{json.dumps(class_spec.get('properties', {}), indent=2, ensure_ascii=False)}

【类方法】
{json.dumps(class_spec.get('methods', []), indent=2, ensure_ascii=False)}

请生成完整的类代码。"""
    
    def _build_function_prompt(self, function_spec: Dict[str, Any]) -> str:
        """构建函数生成提示词"""
        params = function_spec.get('parameters', [])
        params_str = ', '.join([
            f"{p.get('name')}: {p.get('type', 'Any')}"
            for p in params
        ])
        
        return f"""请生成一个Python函数，要求如下：

【函数信息】
- 函数名: {function_spec.get('name', 'new_function')}
- 描述: {function_spec.get('description', '')}
- 返回类型: {function_spec.get('return_type', 'Any')}

【函数参数】
{params_str}

【参数说明】
{json.dumps([{p['name']: p.get('description', '')} for p in params], indent=2, ensure_ascii=False)}

【返回值说明】
{function_spec.get('return_description', '')}

请生成完整的函数代码。"""
    
    def _build_optimization_prompt(self, code: str, optimization_type: str) -> str:
        """构建优化提示词"""
        type_descriptions = {
            'performance': '性能优化 - 提高执行效率，减少资源消耗',
            'readability': '可读性优化 - 提高代码清晰度，改善代码结构',
            'security': '安全优化 - 增强代码安全性，修复潜在漏洞'
        }
        
        return f"""请优化以下Python代码，优化目标: {type_descriptions.get(optimization_type, optimization_type)}

【原始代码】
```python
{code}
```

【优化要求】
1. 保持原有功能不变
2. 提高代码质量
3. 添加必要的注释
4. 遵循最佳实践

请提供优化后的代码。"""
    
    def _build_completion_prompt(self, partial_code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """构建代码补全提示词"""
        context_info = ""
        if context:
            context_info = f"\n【上下文信息】\n{json.dumps(context, indent=2, ensure_ascii=False)}"
        
        return f"""请补全以下Python代码：

【上下文】{context_info}

【部分代码】
```python
{partial_code}
```

请提供补全后的完整代码。"""
    
    def _call_ai_model(self, prompt: str) -> str:
        """调用AI模型
        
        Args:
            prompt: 提示词
            
        Returns:
            AI响应
        """
        # 这里是模拟AI调用，实际使用时需要集成真实的AI API
        # 例如 OpenAI API、Claude API 等
        
        logger.debug(f"调用AI模型，提示词长度: {len(prompt)}")
        
        # 模拟响应
        mock_response = self._mock_ai_response(prompt)
        
        return mock_response
    
    def _mock_ai_response(self, prompt: str) -> str:
        """模拟AI响应（用于测试）"""
        
        if '设备驱动' in prompt or 'device' in prompt.lower():
            return '''```python
from shared.drivers.base.base_device import BaseDevice
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GeneratedDevice(BaseDevice):
    """生成的设备驱动"""
    
    def __init__(self, driver_id: str = 'generated_device', protocol=None, 
                 platform_device=None, **kwargs):
        super().__init__(driver_id, protocol, **kwargs)
        self.protocol = protocol
        self.platform_device = platform_device
        self._device_state = {}
    
    def connect(self) -> bool:
        """连接设备"""
        try:
            self._device_status = "connecting"
            
            if not self.protocol.is_connected:
                if not self.protocol.connect():
                    self._device_status = "fault"
                    if self.platform_device:
                        self.platform_device.disconnect()
                    return False
            
            self._is_connected = True
            self._device_status = "connected"
            
            if self.platform_device:
                self.platform_device.connect()
            
            logger.info(f"设备连接成功: {self.driver_id}")
            return True
        except Exception as e:
            logger.error(f"设备连接失败: {e}")
            self._device_status = "fault"
            self.increment_error()
            return False
    
    def disconnect(self):
        """断开设备连接"""
        self._is_connected = False
        self._device_status = "disconnected"
        
        if self.protocol:
            self.protocol.disconnect()
        
        if self.platform_device:
            self.platform_device.disconnect()
        
        logger.info(f"设备已断开: {self.driver_id}")
    
    def read_data(self) -> Dict[str, Any]:
        """读取设备数据"""
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            data = {}
            
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return data
        except Exception as e:
            logger.error(f"读取数据失败: {e}")
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            raise
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据"""
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return True
        except Exception as e:
            logger.error(f"写入数据失败: {e}")
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """设备健康检查"""
        base = super().health_check()
        
        try:
            if self.is_connected:
                base.update({
                    'device_status': self._device_status,
                    'device_state': self._device_state
                })
        except Exception as e:
            base['health_status'] = 'error'
            base['error_message'] = str(e)
        
        return base
```'''
        
        elif '类' in prompt or 'class' in prompt.lower():
            return '''```python
from typing import Dict, Any, Optional, List

class GeneratedClass:
    """生成的类"""
    
    def __init__(self, **kwargs):
        """初始化"""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def method1(self) -> Any:
        """方法1"""
        pass
    
    def method2(self, param: str) -> bool:
        """方法2
        
        Args:
            param: 参数
            
        Returns:
            结果
        """
        pass
```'''
        
        else:
            return '''```python
# 生成的代码示例
def generated_function(param: str) -> str:
    """生成的函数
    
    Args:
        param: 输入参数
        
    Returns:
        输出结果
    """
    return param.upper()
```'''
    
    def _extract_code(self, response: str) -> str:
        """从响应中提取代码
        
        Args:
            response: AI响应
            
        Returns:
            提取的代码
        """
        # 提取markdown代码块
        if '```python' in response:
            start = response.find('```python') + 9
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        elif '```' in response:
            start = response.find('```') + 3
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        
        return response.strip()
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息
        
        Returns:
            统计数据
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'requests_made': 0,
            'tokens_used': 0,
            'errors': 0
        }