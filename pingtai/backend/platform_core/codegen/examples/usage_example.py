"""
使用代码生成系统生成DG811驱动 - 使用示例

【目的】
- 演示如何使用扩展后的代码生成系统
- 展示通用设备规范的使用
- 生成SCPI设备驱动

【使用步骤】
1. 准备设备规范（DG811_SPEC）
2. 初始化代码生成引擎
3. 调用生成方法
4. 查看生成的代码
"""
import sys
from pathlib import Path

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from platform.codegen.generator.engine import GeneratorEngine
from platform.codegen.template_engine.jinja2_engine import Jinja2Engine
from platform.codegen.core.config import CodeGenConfig
from platform.codegen.examples.dg811_spec import DG811_SPEC


def generate_dg811_driver():
    """生成DG811驱动"""
    
    print("=" * 70)
    print("使用代码生成系统生成DG811驱动")
    print("=" * 70)
    
    # 1. 创建平台配置
    print("\n[1/4] 创建平台配置...")
    config = CodeGenConfig()
    config.base_path = project_root
    config.generator.output_dir = 'backend'
    config.generator.overwrite = True
    config.generator.format_code = True
    config.generator.validate_output = True
    print("✓ 平台配置创建完成")
    
    # 2. 创建模板引擎
    print("\n[2/4] 创建模板引擎...")
    template_engine = Jinja2Engine(config)
    print("✓ 模板引擎创建完成")
    
    # 3. 创建代码生成引擎
    print("\n[3/4] 创建代码生成引擎...")
    generator = GeneratorEngine(config, template_engine)
    print("✓ 代码生成引擎创建完成")
    
    # 4. 生成设备驱动
    print("\n[4/4] 生成设备驱动...")
    print(f"设备名称: {DG811_SPEC['device_name']}")
    print(f"类名: {DG811_SPEC['class_name']}")
    print(f"协议: {DG811_SPEC['protocol']['type']}")
    print(f"通信: {DG811_SPEC['communication']['type']}")
    print(f"通道: {DG811_SPEC['channels']}")
    
    try:
        result = generator.generate(DG811_SPEC, type='device')
        
        print("\n" + "=" * 70)
        print("生成结果")
        print("=" * 70)
        
        print(f"\n成功: {result.get('success', False)}")
        print(f"设备名称: {result.get('device_name', 'N/A')}")
        print(f"类名: {result.get('class_name', 'N/A')}")
        
        print(f"\n生成的文件:")
        for file_info in result.get('files', []):
            print(f"  - {file_info['path']}")
            print(f"    状态: {file_info['status']}")
            if 'lines' in file_info:
                print(f"    行数: {file_info['lines']}")
        
        print(f"\n统计信息:")
        stats = result.get('stats', {})
        print(f"  生成文件: {stats.get('files_generated', 0)}")
        print(f"  跳过文件: {stats.get('files_skipped', 0)}")
        print(f"  覆盖文件: {stats.get('files_overwritten', 0)}")
        print(f"  总行数: {stats.get('total_lines', 0)}")
        
        print("\n✓ 代码生成完成！")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 代码生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    try:
        success = generate_dg811_driver()
        
        if success:
            print("\n" + "=" * 70)
            print("下一步")
            print("=" * 70)
            print("\n1. 查看生成的代码:")
            print(f"   backend/projects/encoder_test/drivers/device/waveform_generator/waveform_generator.py")
            print("\n2. 运行测试:")
            print(f"   python backend/tests/device/test_waveform_generator.py")
            print("\n3. 集成到项目:")
            print(f"   在需要使用的地方导入生成的驱动")
            
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n\n生成被用户中断")
        return 1
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())