"""
代码生成平台使用示例

【示例说明】
演示如何使用代码生成平台生成设备驱动代码
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from platform.codegen import CodeGenPlatform, CodeGenConfig


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)
    
    # 创建配置
    config = CodeGenConfig(
        project_name="device_generation_demo",
        debug=True
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 生成设备规范
        device_spec = {
            'type': 'device',
            'name': 'temperature_sensor',
            'manufacturer': '西门子',
            'model': 'SITRANS T',
            'protocol': 'modbus_rtu',
            'communication': 'rs485',
            'description': '工业温度传感器',
            'parameters': {
                'temperature_range': (-40, 200),
                'accuracy': 0.1,
                'response_time': 1.0
            },
            'methods': [
                {
                    'name': 'get_temperature',
                    'description': '获取当前温度',
                    'parameters': [],
                    'return_type': 'float',
                    'return_description': '温度值（摄氏度）'
                },
                {
                    'name': 'set_calibration',
                    'description': '设置校准参数',
                    'parameters': [
                        {'name': 'offset', 'type': 'float', 'description': '偏移量'},
                        {'name': 'scale', 'type': 'float', 'description': '缩放因子'}
                    ],
                    'return_type': 'bool',
                    'return_description': '是否设置成功'
                }
            ]
        }
        
        # 生成代码
        result = platform.generate(device_spec)
        
        print(f"生成结果: {result['message']}")
        print(f"生成文件数: {result['files_count']}")
        print(f"统计信息: {result['stats']}")


def example_2_custom_config():
    """示例2: 自定义配置"""
    print("\n" + "=" * 60)
    print("示例2: 自定义配置")
    print("=" * 60)
    
    # 创建自定义配置
    config = CodeGenConfig(
        project_name="custom_device_demo",
        debug=True,
        template_engine={
            'engine_type': 'jinja2',
            'cache_enabled': True,
            'cache_size': 50
        },
        generator={
            'output_dir': 'custom_output',
            'overwrite': True,
            'format_code': True,
            'validate_output': True
        }
    )
    
    # 创建平台实例
    platform = CodeGenPlatform(config)
    platform.initialize()
    
    try:
        # 生成设备
        device_spec = {
            'type': 'device',
            'name': 'pressure_sensor',
            'manufacturer': '霍尼韦尔',
            'model': 'Honeywell PPT',
            'protocol': 'modbus_rtu',
            'communication': 'rs485',
            'description': '高精度压力传感器'
        }
        
        result = platform.generate(device_spec)
        print(f"生成完成: {result['message']}")
        
    finally:
        platform.shutdown()


def example_3_scaffold_generation():
    """示例3: 生成项目脚手架"""
    print("\n" + "=" * 60)
    print("示例3: 生成项目脚手架")
    print("=" * 60)
    
    # 创建配置
    config = CodeGenConfig(
        project_name="scaffold_demo",
        debug=True
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 创建标准项目脚手架
        project_spec = {
            'type': 'standard',
            'name': 'my_industrial_project',
            'description': '我的工业自动化项目'
        }
        
        result = platform.create_scaffold(project_spec)
        print(f"脚手架创建完成: {result['message']}")
        print(f"创建目录数: {result['stats']['directories_created']}")
        print(f"创建文件数: {result['stats']['files_created']}")


def example_4_code_validation():
    """示例4: 代码验证"""
    print("\n" + "=" * 60)
    print("示例4: 代码验证")
    print("=" * 60)
    
    # 创建配置（启用AST模块）
    config = CodeGenConfig(
        project_name="validation_demo",
        debug=True,
        ast={
            'enabled': True,
            'language': 'python',
            'validate_syntax': True,
            'optimize_ast': True
        }
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 测试代码
        test_code = '''
def hello_world():
    """打印Hello World"""
    print("Hello, World!")
    return True

class TestClass:
    """测试类"""
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
'''
        
        # 验证代码
        validation_result = platform.validate_code(test_code)
        print(f"验证结果: {validation_result['valid']}")
        print(f"错误信息: {validation_result.get('errors', [])}")
        print(f"警告信息: {validation_result.get('warnings', [])}")
        
        # 分析代码
        analysis_result = platform.validate_code(test_code)  # 使用相同的接口
        print(f"代码分析完成")


def example_5_device_with_registers():
    """示例5: 生成带寄存器的设备"""
    print("\n" + "=" * 60)
    print("示例5: 生成带寄存器的设备")
    print("=" * 60)
    
    # 创建配置
    config = CodeGenConfig(
        project_name="register_device_demo",
        debug=True
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 生成带寄存器定义的设备
        device_spec = {
            'type': 'device',
            'name': 'motor_controller',
            'manufacturer': '西门子',
            'model': 'SINAMICS V90',
            'protocol': 'modbus_rtu',
            'communication': 'rs485',
            'description': '伺服电机控制器',
            'registers': {
                'CONTROL_WORD': 0,
                'STATUS_WORD': 1,
                'VELOCITY_SETPOINT': 2,
                'VELOCITY_ACTUAL': 3,
                'POSITION_ACTUAL': 4,
                'TORQUE_ACTUAL': 5
            },
            'read_registers': ['STATUS_WORD', 'VELOCITY_ACTUAL', 'POSITION_ACTUAL', 'TORQUE_ACTUAL'],
            'write_registers': ['CONTROL_WORD', 'VELOCITY_SETPOINT'],
            'status_registers': ['STATUS_WORD'],
            'reset_command': 'RESET',
            'init_commands': ['ENABLE', 'CLEAR_FAULTS'],
            'methods': [
                {
                    'name': 'start_motor',
                    'description': '启动电机',
                    'parameters': [
                        {'name': 'velocity', 'type': 'float', 'description': '速度'}
                    ],
                    'return_type': 'bool',
                    'return_description': '是否启动成功'
                },
                {
                    'name': 'stop_motor',
                    'description': '停止电机',
                    'parameters': [],
                    'return_type': 'bool',
                    'return_description': '是否停止成功'
                }
            ]
        }
        
        result = platform.generate(device_spec)
        print(f"电机控制器生成完成: {result['message']}")


def example_6_ai_code_generation():
    """示例6: AI代码生成（如果启用）"""
    print("\n" + "=" * 60)
    print("示例6: AI代码生成")
    print("=" * 60)
    
    # 创建配置（启用AI模块）
    config = CodeGenConfig(
        project_name="ai_codegen_demo",
        debug=True,
        ai={
            'enabled': True,
            'model': 'gpt-4',
            'api_key': 'your-api-key-here',  # 需要配置真实的API密钥
            'max_tokens': 2000,
            'temperature': 0.7
        }
    )
    
    # 创建平台实例
    platform = CodeGenPlatform(config)
    platform.initialize()
    
    try:
        # 检查AI模块是否可用
        if platform.has_module('ai'):
            # 使用AI生成设备代码
            device_spec = {
                'name': 'ai_generated_device',
                'manufacturer': 'AI Generated',
                'model': 'AI-Model-1',
                'protocol': 'modbus_rtu',
                'communication': 'rs485',
                'description': 'AI生成的设备'
            }
            
            # 注意：这里需要配置真实的AI API密钥
            # code = platform.ai_generate_device(device_spec)
            # print(f"AI生成代码长度: {len(code)}")
            
            print("AI代码生成功能已启用（需要配置API密钥）")
        else:
            print("AI模块未启用或不可用")
            
    finally:
        platform.shutdown()


def example_7_batch_generation():
    """示例7: 批量生成设备"""
    print("\n" + "=" * 60)
    print("示例7: 批量生成设备")
    print("=" * 60)
    
    # 创建配置
    config = CodeGenConfig(
        project_name="batch_generation_demo",
        debug=True
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 定义多个设备
        devices = [
            {
                'type': 'device',
                'name': 'temperature_sensor',
                'manufacturer': '西门子',
                'model': 'SITRANS T',
                'protocol': 'modbus_rtu',
                'communication': 'rs485',
                'description': '温度传感器'
            },
            {
                'type': 'device',
                'name': 'humidity_sensor',
                'manufacturer': '霍尼韦尔',
                'model': 'HIH-4000',
                'protocol': 'modbus_rtu',
                'communication': 'rs485',
                'description': '湿度传感器'
            },
            {
                'type': 'device',
                'name': 'pressure_sensor',
                'manufacturer': '博世',
                'model': 'BMP280',
                'protocol': 'modbus_rtu',
                'communication': 'rs485',
                'description': '压力传感器'
            }
        ]
        
        # 批量生成
        results = []
        for device_spec in devices:
            result = platform.generate(device_spec)
            results.append(result)
            print(f"生成 {device_spec['name']}: {result['message']}")
        
        # 统计
        total_files = sum(r['stats']['files_generated'] for r in results)
        print(f"\n总计生成 {total_files} 个文件")


def main():
    """主函数"""
    print("代码生成平台使用示例")
    print("=" * 60)
    
    # 运行示例
    examples = [
        example_1_basic_usage,
        example_2_custom_config,
        example_3_scaffold_generation,
        example_4_code_validation,
        example_5_device_with_registers,
        example_6_ai_code_generation,
        example_7_batch_generation
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"示例执行失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("所有示例执行完成")
    print("=" * 60)


if __name__ == '__main__':
    main()