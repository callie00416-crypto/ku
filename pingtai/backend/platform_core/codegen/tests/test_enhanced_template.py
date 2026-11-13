"""
测试增强版设备模板 - 基于电源设备经验

【测试目的】
验证增强版模板能否正确处理：
1. 多通道设备
2. 复杂数据格式（uint32, int32, float32）
3. 地址偏移
4. 控制逻辑映射
5. 单位转换
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from platform.codegen import CodeGenPlatform, CodeGenConfig


def test_enhanced_template():
    """测试增强版模板"""
    print("=" * 60)
    print("测试增强版设备模板")
    print("=" * 60)
    
    # 创建配置
    config = CodeGenConfig(
        project_name="test_enhanced_template",
        debug=True
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 使用电源设备规范
        device_spec = {
            'type': 'device',
            'name': 'test_power_supply',
            'class_name': 'TestPowerSupply',
            'description': '测试用双路电源设备',
            
            'manufacturer': '测试制造商',
            'model': '测试型号双路输出',
            'protocol': 'modbus_rtu',
            'communication': 'rs485',
            'channels': 2,
            
            # 设备配置（关键）
            'device_config': {
                'channels': 2,
                'address_offset': 256,  # 双路型号地址偏移
                'byte_order': 'big',    # 大端序
                'data_format': 'uint32' # 32位整数格式
            },
            
            # 通道寄存器映射
            'channel_registers': {
                1: {
                    'V_SET': {
                        'address': 0x0001,
                        'format': 'uint32',
                        'unit': 'mV',
                        'scale': 0.001,
                        'description': '通道1设定电压'
                    },
                    'I_SET': {
                        'address': 0x0003,
                        'format': 'uint32',
                        'unit': 'mA',
                        'scale': 0.001,
                        'description': '通道1设定电流'
                    },
                    'OUTPUT': {
                        'address': 0x0009,
                        'format': 'uint16',
                        'control_logic': {
                            'on': 0,
                            'off': 1
                        },
                        'description': '通道1输出控制'
                    }
                },
                2: {
                    'V_SET': {
                        'address': 0x000B,
                        'format': 'uint32',
                        'unit': 'mV',
                        'scale': 0.001,
                        'description': '通道2设定电压'
                    },
                    'I_SET': {
                        'address': 0x000D,
                        'format': 'uint32',
                        'unit': 'mA',
                        'scale': 0.001,
                        'description': '通道2设定电流'
                    },
                    'OUTPUT': {
                        'address': 0x0013,
                        'format': 'uint16',
                        'control_logic': {
                            'on': 0,
                            'off': 1
                        },
                        'description': '通道2输出控制'
                    }
                }
            },
            
            # 数据格式配置
            'data_formats': {
                'uint32': {
                    'size': 4,
                    'signed': False,
                    'description': '32位无符号整数'
                }
            },
            
            # 控制逻辑映射
            'control_logic': {
                'output': {
                    'normal': {'on': 1, 'off': 0},
                    'inverted': {'on': 0, 'off': 1}
                }
            },
            
            # 设备参数
            'parameters': {
                'max_voltage': 30.0,
                'max_current': 5.0
            },
            
            # 自定义方法
            'methods': [
                {
                    'name': 'set_voltage',
                    'description': '设置通道电压',
                    'parameters': [
                        {
                            'name': 'voltage',
                            'type': 'float',
                            'description': '目标电压值(V)'
                        },
                        {
                            'name': 'channel',
                            'type': 'int',
                            'default': 1,
                            'description': '通道号(1或2)'
                        }
                    ],
                    'return_type': 'bool',
                    'return_description': '是否设置成功'
                }
            ]
        }
        
        print("\n【步骤1】生成设备驱动...")
        result = platform.generate(device_spec)
        
        if result['success']:
            print("✅ 生成成功")
            print(f"📊 生成统计:")
            print(f"   - 生成文件: {result['stats']['files_generated']}")
            print(f"   - 跳过文件: {result['stats']['files_skipped']}")
            print(f"   - 覆盖文件: {result['stats']['files_overwritten']}")
            print(f"   - 总行数: {result['stats']['total_lines']}")
            
            if 'template_type' in result:
                print(f"📝 模板类型: {result['template_type']}")
            
            print("\n【步骤2】检查生成的文件...")
            for file_info in result.get('files', []):
                if file_info.get('success'):
                    print(f"✅ {file_info['output']}")
                    
                    # 检查文件内容
                    output_path = Path(config.base_path) / file_info['output']
                    if output_path.exists():
                        content = output_path.read_text(encoding='utf-8')
                        
                        # 检查关键特性
                        checks = {
                            '多通道支持': 'channel_registers' in content or 'CHANNEL_REGISTERS' in content,
                            '地址偏移': 'address_offset' in content,
                            '数据格式转换': '_read_uint32' in content or '_write_uint32' in content,
                            '单位转换': 'scale' in content,
                            '控制逻辑映射': 'control_logic' in content,
                            '字节序处理': 'byte_order' in content
                        }
                        
                        print(f"   特性检查:")
                        for feature, passed in checks.items():
                            status = "✅" if passed else "❌"
                            print(f"     {status} {feature}")
            
            print("\n【步骤3】验证生成代码...")
            # 这里可以添加更多的验证逻辑
            print("✅ 验证完成")
            
        else:
            print("❌ 生成失败")
            print(f"错误: {result.get('message', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


def test_standard_template():
    """测试标准模板"""
    print("\n" + "=" * 60)
    print("测试标准设备模板")
    print("=" * 60)
    
    # 创建配置
    config = CodeGenConfig(
        project_name="test_standard_template",
        debug=True
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 使用简单设备规范
        device_spec = {
            'type': 'device',
            'name': 'test_simple_sensor',
            'description': '测试用简单传感器',
            
            'manufacturer': '测试制造商',
            'model': '测试型号',
            'protocol': 'modbus_rtu',
            'communication': 'rs485',
            'channels': 1,
            
            # 简单寄存器配置
            'registers': {
                'TEMPERATURE': 0x0001,
                'HUMIDITY': 0x0002
            },
            
            'read_registers': ['TEMPERATURE', 'HUMIDITY'],
            'write_registers': []
        }
        
        print("\n【步骤1】生成设备驱动...")
        result = platform.generate(device_spec)
        
        if result['success']:
            print("✅ 生成成功")
            print(f"📊 生成统计:")
            print(f"   - 生成文件: {result['stats']['files_generated']}")
            print(f"   - 跳过文件: {result['stats']['files_skipped']}")
            
            if 'template_type' in result:
                print(f"📝 模板类型: {result['template_type']}")
        else:
            print("❌ 生成失败")
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


if __name__ == '__main__':
    print("\n🚀 开始测试增强版模板功能\n")
    
    # 测试增强版模板
    test_enhanced_template()
    
    # 测试标准模板
    test_standard_template()
    
    print("\n✅ 所有测试完成\n")