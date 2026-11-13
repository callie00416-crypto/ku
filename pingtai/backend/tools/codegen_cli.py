"""
代码生成平台命令行工具 - CodeGen CLI

【功能说明】
提供命令行接口使用代码生成平台
"""
import argparse
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from platform_core.codegen import CodeGenPlatform, CodeGenConfig


def cmd_generate(args):
    """生成代码命令
    
    【经验教训】
    - 支持从设备规范文件生成
    - 支持增强版模板自动选择
    - 支持多通道设备配置
    """
    print(f"生成设备: {args.name}")
    
    # 创建配置
    config = CodeGenConfig(
        project_name=args.project or "codegen_project",
        debug=args.debug
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 如果提供了规范文件，从文件加载
        if args.spec_file:
            print(f"从规范文件加载: {args.spec_file}")
            with open(args.spec_file, 'r', encoding='utf-8') as f:
                device_spec = json.load(f)
        else:
            # 构建设备规范
            device_spec = {
                'type': 'device',
                'name': args.name,
                'manufacturer': args.manufacturer or 'Unknown',
                'model': args.model or 'Unknown',
                'protocol': args.protocol or 'modbus_rtu',
                'communication': args.communication or 'rs485',
                'description': args.description or ''
            }
            
            # 添加参数
            if args.parameters:
                device_spec['parameters'] = json.loads(args.parameters)
            
            # 添加方法
            if args.methods:
                device_spec['methods'] = json.loads(args.methods)
        
        # 生成代码
        result = platform.generate(device_spec)
        
        print(f"✅ {result['message']}")
        print(f"📊 生成统计:")
        print(f"   - 生成文件: {result['stats']['files_generated']}")
        print(f"   - 跳过文件: {result['stats']['files_skipped']}")
        print(f"   - 覆盖文件: {result['stats']['files_overwritten']}")
        print(f"   - 总行数: {result['stats']['total_lines']}")
        
        # 显示使用的模板类型
        if 'template_type' in result:
            print(f"📝 模板类型: {result['template_type']}")


def cmd_scaffold(args):
    """创建脚手架命令"""
    print(f"创建项目脚手架: {args.name}")
    
    # 创建配置
    config = CodeGenConfig(
        project_name=args.project or "scaffold_project",
        debug=args.debug
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 构建项目规范
        project_spec = {
            'type': args.type or 'standard',
            'name': args.name,
            'description': args.description or ''
        }
        
        # 创建脚手架
        result = platform.create_scaffold(project_spec)
        
        print(f"✅ {result['message']}")
        print(f"📊 创建统计:")
        print(f"   - 创建目录: {result['stats']['directories_created']}")
        print(f"   - 创建文件: {result['stats']['files_created']}")
        print(f"   - 总大小: {result['stats']['total_size']} 字节")


def cmd_validate(args):
    """验证代码命令"""
    print(f"验证代码: {args.file}")
    
    # 读取代码文件
    with open(args.file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 创建配置
    config = CodeGenConfig(
        project_name="validation_project",
        debug=args.debug,
        ast={
            'enabled': True,
            'language': args.language or 'python',
            'validate_syntax': True,
            'optimize_ast': False
        }
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 验证代码
        result = platform.validate_code(code, args.language or 'python')
        
        if result['valid']:
            print("✅ 代码验证通过")
        else:
            print("❌ 代码验证失败")
        
        # 显示错误和警告
        if result.get('errors'):
            print(f"\n❌ 错误 ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"   - {error}")
        
        if result.get('warnings'):
            print(f"\n⚠️  警告 ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"   - {warning}")


def cmd_analyze(args):
    """分析代码命令"""
    print(f"分析代码: {args.file}")
    
    # 读取代码文件
    with open(args.file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 创建配置
    config = CodeGenConfig(
        project_name="analysis_project",
        debug=args.debug,
        ast={
            'enabled': True,
            'language': args.language or 'python'
        }
    )
    
    # 创建平台实例
    with CodeGenPlatform(config) as platform:
        # 分析代码
        result = platform.validate_code(code, args.language or 'python')  # 使用validate接口
        
        print(f"📊 代码分析结果:")
        print(f"   - 函数数量: {len(result.get('functions', []))}")
        print(f"   - 类数量: {len(result.get('classes', []))}")
        print(f"   - 导入数量: {len(result.get('imports', []))}")
        print(f"   - 代码行数: {result.get('lines_of_code', 0)}")
        print(f"   - 圈复杂度: {result.get('complexity', 0)}")


def cmd_config(args):
    """配置管理命令"""
    if args.action == 'create':
        # 创建默认配置文件
        config = CodeGenConfig(
            project_name=args.project or "my_project",
            debug=False
        )
        
        config_path = Path(args.output) if args.output else Path.cwd() / 'codegen_config.json'
        config.save_to_file(config_path)
        
        print(f"✅ 配置文件已创建: {config_path}")
    
    elif args.action == 'validate':
        # 验证配置文件
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"❌ 配置文件不存在: {config_path}")
            return
        
        try:
            config = CodeGenConfig.from_file(config_path)
            if config.validate():
                print(f"✅ 配置文件有效: {config_path}")
            else:
                print(f"❌ 配置文件无效: {config_path}")
        except Exception as e:
            print(f"❌ 配置文件解析失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='工业自动化代码生成平台',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 生成设备驱动
  python codegen_cli.py generate temperature_sensor --manufacturer "西门子"
  
  # 创建项目脚手架
  python codegen_cli.py scaffold my_project --type standard
  
  # 验证代码
  python codegen_cli.py validate my_device.py
  
  # 创建配置文件
  python codegen_cli.py config create --output my_config.json
        '''
    )
    
    # 全局参数
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--project', help='项目名称')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # generate 命令
    generate_parser = subparsers.add_parser('generate', help='生成代码')
    generate_parser.add_argument('name', help='设备名称')
    generate_parser.add_argument('--spec-file', help='设备规范文件路径 (JSON)')
    generate_parser.add_argument('--manufacturer', help='制造商')
    generate_parser.add_argument('--model', help='型号')
    generate_parser.add_argument('--protocol', help='通信协议')
    generate_parser.add_argument('--communication', help='通信方式')
    generate_parser.add_argument('--description', help='设备描述')
    generate_parser.add_argument('--parameters', help='设备参数 (JSON)')
    generate_parser.add_argument('--methods', help='设备方法 (JSON)')
    
    # scaffold 命令
    scaffold_parser = subparsers.add_parser('scaffold', help='创建项目脚手架')
    scaffold_parser.add_argument('name', help='项目名称')
    scaffold_parser.add_argument('--type', help='项目类型 (standard, device, platform)')
    scaffold_parser.add_argument('--description', help='项目描述')
    
    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证代码')
    validate_parser.add_argument('file', help='代码文件路径')
    validate_parser.add_argument('--language', help='编程语言')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析代码')
    analyze_parser.add_argument('file', help='代码文件路径')
    analyze_parser.add_argument('--language', help='编程语言')
    
    # config 命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_parser.add_argument('action', choices=['create', 'validate'], help='操作类型')
    config_parser.add_argument('--config', help='配置文件路径')
    config_parser.add_argument('--output', help='输出文件路径')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 执行命令
    try:
        if args.command == 'generate':
            cmd_generate(args)
        elif args.command == 'scaffold':
            cmd_scaffold(args)
        elif args.command == 'validate':
            cmd_validate(args)
        elif args.command == 'analyze':
            cmd_analyze(args)
        elif args.command == 'config':
            cmd_config(args)
        
        return 0
    
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())