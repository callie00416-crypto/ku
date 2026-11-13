"""
调试脚本 - 运行编码器上断电测试用例
"""
import sys
import os

# 添加 backend 到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入测试用例
from projects.encoder_test.core.testcase.encoder.encoder_power_cycle_case import (
    EncoderPowerCycleCase,
    EncoderSinglePowerCycleCase,
    MockPowerAmplifier,
    MockWaveformGenerator,
    MockEncoder
)


def test_single_power_cycle():
    """测试单次上断电"""
    print("\n" + "="*60)
    print("测试单次上断电循环")
    print("="*60)
    
    case = EncoderSinglePowerCycleCase(
        power_amplifier=MockPowerAmplifier(),
        encoder=MockEncoder(),
        case_id="single_power_cycle_debug",
        use_mock=True
    )
    
    case.set_parameter('power_off_delay', 1.0)
    case.set_parameter('power_on_delay', 2.0)
    case.set_parameter('tolerance', 0.5)
    
    result = case.execute()
    
    print(f"\n测试结果: {result.status.value}")
    print(f"测试消息: {result.message}")
    if result.data:
        print(f"测试数据: {result.data}")
    
    return result


def test_multiple_power_cycle():
    """测试多次上断电循环"""
    print("\n" + "="*60)
    print("测试多次上断电循环 (3次)")
    print("="*60)
    
    case = EncoderPowerCycleCase(
        power_amplifier=MockPowerAmplifier(),
        waveform_generator=MockWaveformGenerator(),
        encoder=MockEncoder(),
        case_id="multi_power_cycle_debug",
        use_mock=True
    )
    
    case.set_parameter('cycle_count', 3)
    case.set_parameter('power_off_delay', 1.0)
    case.set_parameter('power_on_delay', 2.0)
    case.set_parameter('tolerance', 0.5)
    case.set_parameter('waveform_type', 'SIN')
    case.set_parameter('frequency', 1000.0)
    case.set_parameter('amplitude', 5.0)
    case.set_parameter('gain', 20)
    
    result = case.execute()
    
    print(f"\n测试结果: {result.status.value}")
    print(f"测试消息: {result.message}")
    if result.data:
        print(f"测试数据: {result.data}")
    
    return result


if __name__ == '__main__':
    try:
        # 运行单次测试
        result1 = test_single_power_cycle()
        
        # 运行多次测试
        result2 = test_multiple_power_cycle()
        
        print("\n" + "="*60)
        print("所有测试完成")
        print("="*60)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)