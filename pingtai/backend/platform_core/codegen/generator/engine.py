"""
代码生成引擎 - Generator Engine

【职责】
- 核心代码生成逻辑
- 协调模板引擎和DSL
- 文件生成和管理
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
import json

from ..template_engine.engine import TemplateEngine


logger = logging.getLogger(__name__)


class GeneratorEngine:
    """代码生成引擎
    
    【职责】
- 根据规范生成代码
- 协调模板引擎
- 管理输出文件
- 支持增量生成
    """
    
    def __init__(self, config, template_engine: TemplateEngine):
        """
        Args:
            config: 平台配置
            template_engine: 模板引擎实例
        """
        self.config = config
        self.template_engine = template_engine
        self.output_dir = Path(config.base_path) / config.generator.output_dir
        self.overwrite = config.generator.overwrite
        self.format_code = config.generator.format_code
        self.validate_output = config.generator.validate_output
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成统计
        self.stats = {
            'files_generated': 0,
            'files_skipped': 0,
            'files_overwritten': 0,
            'total_lines': 0
        }
        
        logger.info(f"代码生成引擎初始化完成，输出目录: {self.output_dir}")
    
    def generate(self, spec: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成代码
        
        Args:
            spec: 生成规范
            **kwargs: 额外参数
            
        Returns:
            生成结果
        """
        try:
            logger.info(f"开始生成代码: {spec.get('name', 'unknown')}")
            
            # 重置统计
            self.stats = {
                'files_generated': 0,
                'files_skipped': 0,
                'files_overwritten': 0,
                'total_lines': 0
            }
            
            # 解析生成规范
            generator_type = spec.get('type', 'default')
            
            # 根据类型选择生成策略
            if generator_type == 'device':
                result = self._generate_device(spec, **kwargs)
            elif generator_type == 'module':
                result = self._generate_module(spec, **kwargs)
            elif generator_type == 'class':
                result = self._generate_class(spec, **kwargs)
            elif generator_type == 'function':
                result = self._generate_function(spec, **kwargs)
            else:
                result = self._generate_default(spec, **kwargs)
            
            # 添加生成统计
            result['stats'] = self.stats.copy()
            
            logger.info(f"代码生成完成: {self.stats['files_generated']} 个文件")
            return result
            
        except Exception as e:
            logger.error(f"代码生成失败: {e}")
            raise
    
    def _generate_device(self, spec: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成设备驱动代码
        
        【经验教训】
        - 支持多种协议（SCPI、Modbus等）
        - 支持增强版模板（多通道、复杂数据格式）
        - 支持设备规范配置
        - 自动选择合适的模板
        
        Args:
            spec: 设备规范
            **kwargs: 额外参数
            
        Returns:
            生成结果
        """
        device_name = spec.get('device_name', 'new_device')
        class_name = spec.get('class_name', self._to_class_name(device_name))
        
        # 准备上下文
        context = {
            'device_name': device_name,
            'class_name': class_name,
            'module_path': f'projects.encoder_test.drivers.device.{device_name}.{device_name}',
            'spec': spec,
            'config': self.config,
            **kwargs
        }
        
        # 根据协议类型选择模板
        protocol_type = spec.get('protocol', {}).get('type', 'modbus_rtu')
        
        if protocol_type == 'scpi':
            # SCPI协议使用SCPI模板
            template_name = 'device/device_scpi.py.j2'
            logger.info(f"使用SCPI模板生成设备驱动")
        elif protocol_type == 'custom':
            # 自定义协议使用Custom ASCII模板
            template_name = 'device/device_custom_ascii.py.j2'
            logger.info(f"使用Custom ASCII模板生成设备驱动")
        elif self._should_use_enhanced_template(spec):
            # 复杂设备使用增强版模板
            template_name = 'device/device_enhanced.py.j2'
            logger.info(f"使用增强版模板生成设备驱动")
        else:
            # 简单设备使用标准模板
            template_name = 'device/device.py.j2'
            logger.info(f"使用标准模板生成设备驱动")
        
        # 生成文件列表
        files_to_generate = [
            {
                'template': template_name,
                'output': f'projects/encoder_test/drivers/device/{device_name}/{device_name}.py',
                'context': context
            },
            {
                'template': 'device/__init__.py.j2',
                'output': f'projects/encoder_test/drivers/device/{device_name}/__init__.py',
                'context': context
            },
            {
                'template': 'device/adapter.py.j2',
                'output': f'projects/encoder_test/adapters/{device_name}_adapter.py',
                'context': context
            },
            {
                'template': 'tests/test_device.py.j2',
                'output': f'tests/device/test_{device_name}.py',
                'context': context
            },
            {
                'template': 'tests/test_device_full_link.py.j2',
                'output': f'tests/device/test_{device_name}_full_link.py',
                'context': context
            }
        ]
        
        # 生成文件
        generated_files = []
        for file_spec in files_to_generate:
            try:
                result = self._generate_file(
                    file_spec['template'],
                    file_spec['output'],
                    file_spec['context']
                )
                generated_files.append(result)
            except Exception as e:
                logger.warning(f"文件生成失败 {file_spec['output']}: {e}")
        
        return {
            'success': True,
            'device_name': device_name,
            'class_name': class_name,
            'files': generated_files,
            'message': f'设备 {device_name} 生成完成'
        }
    
    def _generate_module(self, spec: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成模块代码
        
        Args:
            spec: 模块规范
            **kwargs: 额外参数
            
        Returns:
            生成结果
        """
        module_name = spec.get('name', 'new_module')
        
        # 准备上下文
        context = {
            'module_name': module_name,
            'spec': spec,
            'config': self.config,
            **kwargs
        }
        
        # 生成文件
        output_path = f'projects/encoder_test/{module_name}.py'
        result = self._generate_file('module.py.j2', output_path, context)
        
        return {
            'success': True,
            'module_name': module_name,
            'files': [result],
            'message': f'模块 {module_name} 生成完成'
        }
    
    def _generate_class(self, spec: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成类代码
        
        Args:
            spec: 类规范
            **kwargs: 额外参数
            
        Returns:
            生成结果
        """
        class_name = spec.get('name', 'NewClass')
        
        # 准备上下文
        context = {
            'class_name': class_name,
            'spec': spec,
            'config': self.config,
            **kwargs
        }
        
        # 生成代码片段
        code = self.template_engine.render_string(
            self._get_class_template(),
            context
        )
        
        return {
            'success': True,
            'class_name': class_name,
            'code': code,
            'message': f'类 {class_name} 生成完成'
        }
    
    def _generate_function(self, spec: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成函数代码
        
        Args:
            spec: 函数规范
            **kwargs: 额外参数
            
        Returns:
            生成结果
        """
        function_name = spec.get('name', 'new_function')
        
        # 准备上下文
        context = {
            'function_name': function_name,
            'spec': spec,
            'config': self.config,
            **kwargs
        }
        
        # 生成代码片段
        code = self.template_engine.render_string(
            self._get_function_template(),
            context
        )
        
        return {
            'success': True,
            'function_name': function_name,
            'code': code,
            'message': f'函数 {function_name} 生成完成'
        }
    
    def _generate_default(self, spec: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """默认生成策略
        
        Args:
            spec: 生成规范
            **kwargs: 额外参数
            
        Returns:
            生成结果
        """
        # 准备上下文
        context = {
            'spec': spec,
            'config': self.config,
            **kwargs
        }
        
        # 根据规范生成文件
        files = spec.get('files', [])
        generated_files = []
        
        for file_spec in files:
            try:
                result = self._generate_file(
                    file_spec.get('template'),
                    file_spec.get('output'),
                    {**context, **file_spec.get('context', {})}
                )
                generated_files.append(result)
            except Exception as e:
                logger.warning(f"文件生成失败 {file_spec.get('output')}: {e}")
        
        return {
            'success': True,
            'files': generated_files,
            'message': '代码生成完成'
        }
    
    def _generate_file(self, template_name: str, output_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成单个文件
        
        Args:
            template_name: 模板名称
            output_path: 输出路径
            context: 上下文数据
            
        Returns:
            生成结果
        """
        # 渲染模板
        content = self.template_engine.render(template_name, context)
        
        # 格式化代码
        if self.format_code:
            content = self._format_code(content)
        
        # 验证输出
        if self.validate_output:
            self._validate_output(content)
        
        # 确定输出路径
        output_file = self.output_dir / output_path
        
        # 检查文件是否存在
        file_exists = output_file.exists()
        
        # 决定是否覆盖
        if file_exists and not self.overwrite:
            logger.info(f"文件已存在，跳过: {output_path}")
            self.stats['files_skipped'] += 1
            return {
                'path': str(output_file),
                'status': 'skipped',
                'reason': 'file_exists'
            }
        
        # 创建目录
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新统计
        if file_exists:
            self.stats['files_overwritten'] += 1
            status = 'overwritten'
        else:
            self.stats['files_generated'] += 1
            status = 'created'
        
        self.stats['total_lines'] += len(content.splitlines())
        
        logger.info(f"文件生成完成: {output_path} ({status})")
        
        return {
            'path': str(output_file),
            'status': status,
            'lines': len(content.splitlines())
        }
    
    def _format_code(self, code: str) -> str:
        """格式化代码
        
        Args:
            code: 原始代码
            
        Returns:
            格式化后的代码
        """
        try:
            import black
            return black.format_str(code, mode=black.FileMode())
        except ImportError:
            logger.warning("black未安装，跳过代码格式化")
            return code
        except Exception as e:
            logger.warning(f"代码格式化失败: {e}")
            return code
    
    def _validate_output(self, code: str):
        """验证输出代码
        
        Args:
            code: 输出代码
        """
        try:
            import ast
            ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"生成的代码存在语法错误: {e}")
    
    def _to_class_name(self, name: str) -> str:
        """转换为类名
        
        Args:
            name: 原始名称
            
        Returns:
            类名
        """
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _get_class_template(self) -> str:
        """获取类模板"""
        return '''
class {{ class_name }}:
    """{{ spec.description | default('Generated class') }}"""
    
    def __init__(self{% for param in spec.parameters | default([]) %}, {{ param.name }}: {{ param.type | default('Any') }}{% if param.default %} = {{ param.default }}{% endif %}{% endfor %}):
        {% for param in spec.parameters | default([]) %}
        self.{{ param.name }} = {{ param.name }}
        {% endfor %}
    
    {% for method in spec.methods | default([]) %}
    def {{ method.name }}(self{% for param in method.parameters | default([]) %}, {{ param.name }}: {{ param.type | default('Any') }}{% endfor %}) -> {{ method.return_type | default('Any') }}:
        """{{ method.description | default('Generated method') }}"""
        pass
    {% endfor %}
'''
    
    def _get_function_template(self) -> str:
        """获取函数模板"""
        return '''
def {{ function_name }}({% for param in spec.parameters | default([]) %}{{ param.name }}: {{ param.type | default('Any') }}{% if not loop.last %}, {% endif %}{% endfor %}) -> {{ spec.return_type | default('Any') }}:
    """{{ spec.description | default('Generated function') }}
    
    {% for param in spec.parameters | default([]) %}
    Args:
        {{ param.name }}: {{ param.description | default('Parameter') }}
    {% endfor %}
    
    Returns:
        {{ spec.return_description | default('Result') }}
    """
    pass
'''
    
    def get_stats(self) -> Dict[str, int]:
        """获取生成统计
        
        Returns:
            统计数据
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'files_generated': 0,
            'files_skipped': 0,
            'files_overwritten': 0,
            'total_lines': 0
        }
    
    def _should_use_enhanced_template(self, spec: Dict[str, Any]) -> bool:
        """判断是否应该使用增强版模板
        
        【经验教训】
        基于电源设备测试经验，当设备具有以下特征时使用增强版模板：
        - 多通道/多路设备
        - 复杂数据格式（非标准uint16）
        - 需要地址偏移
        - 需要控制逻辑映射
        - 需要单位转换
        
        Args:
            spec: 设备规范
            
        Returns:
            是否使用增强版模板
        """
        # 检查多通道
        if spec.get('channels', 1) > 1:
            logger.info("检测到多通道设备，使用增强版模板")
            return True
        
        # 检查通道寄存器配置
        if 'channel_registers' in spec and spec['channel_registers']:
            logger.info("检测到通道寄存器配置，使用增强版模板")
            return True
        
        # 检查设备配置
        device_config = spec.get('device_config', {})
        if device_config.get('address_offset', 0) != 0:
            logger.info("检测到地址偏移配置，使用增强版模板")
            return True
        
        if device_config.get('byte_order') != 'big':
            logger.info("检测到非大端序配置，使用增强版模板")
            return True
        
        if device_config.get('data_format') not in ['uint16', None]:
            logger.info(f"检测到复杂数据格式 {device_config.get('data_format')}，使用增强版模板")
            return True
        
        # 检查控制逻辑配置
        if 'control_logic' in spec and spec['control_logic']:
            logger.info("检测到控制逻辑配置，使用增强版模板")
            return True
        
        # 检查数据格式配置
        if 'data_formats' in spec and spec['data_formats']:
            logger.info("检测到数据格式配置，使用增强版模板")
            return True
        
        # 默认使用标准模板
        return False