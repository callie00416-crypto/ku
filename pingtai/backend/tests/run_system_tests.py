"""
Django系统测试运行器
运行Runtime和Encoder Test系统的Django集成测试
"""
import os
import sys
import django
import time
import subprocess

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()


def run_runtime_system_tests():
    """运行Runtime系统测试"""
    print("=" * 70)
    print("运行Runtime系统测试")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/test_runtime_system.py', '-v'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("测试超时")
        return False
    except Exception as e:
        print(f"测试执行失败: {e}")
        return False


def run_encoder_test_system_tests():
    """运行Encoder Test系统测试"""
    print("\n" + "=" * 70)
    print("运行Encoder Test系统测试")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/test_encoder_test_system.py', '-v'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("测试超时")
        return False
    except Exception as e:
        print(f"测试执行失败: {e}")
        return False


def run_all_system_tests():
    """运行所有系统测试"""
    start_time = time.time()
    
    results = {
        'runtime_system': run_runtime_system_tests(),
        'encoder_test_system': run_encoder_test_system_tests()
    }
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("系统测试总结")
    print("=" * 70)
    print(f"Runtime系统测试: {'通过' if results['runtime_system'] else '失败'}")
    print(f"Encoder Test系统测试: {'通过' if results['encoder_test_system'] else '失败'}")
    print(f"总执行时间: {elapsed:.2f}秒")
    print("=" * 70)
    
    all_passed = all(results.values())
    print(f"\n总体结果: {'全部通过' if all_passed else '存在失败'}")
    
    return all_passed


def run_specific_test(test_file):
    """运行特定测试文件"""
    print(f"运行测试文件: {test_file}")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', test_file, '-v'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("测试超时")
        return False
    except Exception as e:
        print(f"测试执行失败: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Django系统测试运行器')
    parser.add_argument('--runtime', action='store_true', help='只运行Runtime系统测试')
    parser.add_argument('--encoder', action='store_true', help='只运行Encoder Test系统测试')
    parser.add_argument('--file', type=str, help='运行特定测试文件')
    
    args = parser.parse_args()
    
    if args.file:
        success = run_specific_test(args.file)
    elif args.runtime:
        success = run_runtime_system_tests()
    elif args.encoder:
        success = run_encoder_test_system_tests()
    else:
        success = run_all_system_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()