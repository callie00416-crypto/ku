"""
测试ATA-101B模板渲染
"""
import sys
from pathlib import Path

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from platform.codegen.template_engine.jinja2_engine import Jinja2Engine
from platform.codegen.core.config import CodeGenConfig
from platform.codegen.examples.ata101b_spec import ATA101B_SPEC


def test_template_render():
    """测试模板渲染"""
    
    print("=" * 70)
    print("测试ATA-101B模板渲染")
    print("=" * 70)
    
    # 创建配置
    config = CodeGenConfig()
    config.base_path = project_root
    config.template_engine.template_dir = 'platform/codegen/templates'
    
    # 创建模板引擎
    print("\n[1/3] 创建模板引擎...")
    try:
        template_engine = Jinja2Engine(config)
        print("✓ 模板引擎创建完成")
    except Exception as e:
        print(f"✗ 模板引擎创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 准备上下文
    print("\n[2/3] 准备上下文...")
    context = {
        'device_name': ATA101B_SPEC['device_name'],
        'class_name': ATA101B_SPEC['class_name'],
        'manufacturer': ATA101B_SPEC['manufacturer'],
        'model': ATA101B_SPEC['model'],
        'serial_number': ATA101B_SPEC['serial_number'],
        'firmware_version': ATA101B_SPEC['firmware_version'],
        'protocol': ATA101B_SPEC['protocol'],
        'communication': ATA101B_SPEC['communication'],
        'channels': ATA101B_SPEC['channels'],
        'custom_protocol_config': ATA101B_SPEC['custom_protocol_config'],
        'parameters': ATA101B_SPEC['parameters'],
        'methods': ATA101B_SPEC['methods']
    }
    print("✓ 上下文准备完成")
    
    # 渲染模板
    print("\n[3/3] 渲染模板...")
    try:
        content = template_engine.render('device/device_custom_ascii.py.j2', context)
        print(f"✓ 模板渲染完成，内容长度: {len(content)}")
        
        # 保存到文件
        output_file = project_root / 'backend' / 'projects' / 'encoder_test' / 'drivers' / 'device' / 'power_amplifier' / 'power_amplifier.py'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 文件已保存: {output_file}")
        print(f"  行数: {len(content.splitlines())}")
        
        return True
        
    except Exception as e:
        print(f"✗ 模板渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_template_render()
    sys.exit(0 if success else 1)