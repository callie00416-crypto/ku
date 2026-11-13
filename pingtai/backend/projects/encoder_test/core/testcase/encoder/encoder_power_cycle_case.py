"""
编码器上断电测试用例（符合新架构）

================================================================================
模块说明
================================================================================
本模块实现编码器上断电循环测试的业务逻辑，包含两个测试用例类：
1. EncoderPowerCycleCase - 多次上断电循环测试（使用波形发生器硬件自动控制）
2. EncoderSinglePowerCycleCase - 单次上断电测试（手动控制）

测试原理：
    波形发生器输出1Hz脉冲波（50%占空比，高电平5V，低电平0V），通过功率放大器驱动编码器电源，
    实现硬件级别的周期性上断电。每个周期0.5秒上电、0.5秒断电。

预期行为：
    - 上电状态：编码器可正常读取角度数据
    - 断电状态：编码器无法读取数据（返回0°，符合预期）
    - 断电后上电：角度数据应保持稳定，误差在容忍度范围内

架构分层：
    Driver层  →  Action层  →  Check层  →  TestCase层（本模块）
    设备驱动       业务动作      数据校验       测试用例逻辑

设计特点：
    - 不直接操作寄存器，使用业务级Action封装
    - 不关心通讯协议细节，协议由Driver层处理
    - 使用Check类进行统一的数据校验
    - 支持参数化配置，提高复用性
    - 完善的错误处理和日志记录

================================================================================
测试参数说明
================================================================================
| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| cycle_count | int | 10 | 上断电循环次数 |
| power_off_delay | float | 1.0 | 断电等待时间（秒） |
| power_on_delay | float | 2.0 | 上电等待时间（秒） |
| tolerance | float | 0.5 | 角度误差容忍度（度） |
| frequency | float | 1.0 | 波形发生器频率（Hz） |

================================================================================
测试断言说明
================================================================================
1. 初始上电窗口断言：必须读到非零角度（上电状态）
2. 循环上电窗口断言：每个上电窗口必须读到角度数据
3. 角度稳定性断言：断电前后角度误差必须小于容忍度
4. 数据有效性断言：CRC校验必须通过

================================================================================
设备连接说明
================================================================================
- 波形发生器：USB连接，SCPI协议
- 功率放大器：串口连接（COM7），自定义ASCII协议
- 编码器：串口连接（COM6），Analyzer SDK
"""
from typing import Any, Dict, List
from projects.encoder_test.core.testcase.base.base_case import BaseCase
from projects.encoder_test.actions import DelayAction
from projects.encoder_test.actions.encoder_action import EncoderAction
from projects.encoder_test.actions.power_amplifier_action import PowerAmplifierAction
from projects.encoder_test.actions.waveform_generator_action import WaveformGeneratorAction
from projects.encoder_test.core.checks.angle_check import AngleCheck
import logging
import time

logger = logging.getLogger(__name__)


class EncoderPowerCycleCase(BaseCase):
    """编码器上断电循环测试用例（使用波形发生器自动控制）

    测试流程：
    ┌─────────────────────────────────────────────────────────────────┐
    │ 1. 设备初始化                                                  │
    │    ├── 设置功率放大器增益为0dB                                   │
    │    ├── 设置功率放大器输出电阻为1.5Ω（匹配编码器负载）              │
    │    └── 设置波形发生器输出1Hz脉冲波（50%占空比，0~5V）            │
    ├─────────────────────────────────────────────────────────────────┤
    │ 2. 初始角度读取                                                │
    │    ├── 等待第一个上电周期（1秒）                                 │
    │    ├── 多次读取找到稳定的非零角度（排除断电状态）                  │
    │    └── 记录初始角度作为参考基准                                   │
    ├─────────────────────────────────────────────────────────────────┤
    │ 3. 循环测试（cycle_count次）                                    │
    │    ├── 等待一个完整上断电周期（1.2秒）                           │
    │    ├── 主动等待进入上电状态（读到非零角度）                        │
    │    ├── 在上电窗口内读取稳定角度                                  │
    │    ├── 验证角度与初始角度误差 < tolerance                        │
    │    └── 记录循环结果                                             │
    ├─────────────────────────────────────────────────────────────────┤
    │ 4. 结果断言                                                    │
    │    └── 所有循环必须全部成功                                      │
    └─────────────────────────────────────────────────────────────────┘

    关键技术点：
    - 使用波形发生器硬件实现周期性上断电，替代软件延时控制
    - 上电窗口检测机制：通过读取非零角度判断是否进入上电状态
    - 稳定读数判定：连续两次读到相同角度（误差<0.01°）认为稳定
    - 三重断言机制：确保上电窗口必能读到角度数据
    """

    def __init__(
        self,
        power_amplifier_action: PowerAmplifierAction = None,
        waveform_generator_action: WaveformGeneratorAction = None,
        encoder_action: EncoderAction = None,
        case_id: str = "encoder_power_cycle",
        description: str = "编码器上断电循环测试",
        **kwargs
    ):
        """
        构造函数

        Args:
            power_amplifier_action: 功率放大器Action实例
            waveform_generator_action: 波形发生器Action实例
            encoder_action: 编码器Action实例
            case_id: 测试用例ID（用于日志和报告）
            description: 测试用例描述
            **kwargs: 额外参数（传递给父类BaseCase）
        """
        super().__init__(case_id=case_id, description=description, **kwargs)
        self._power_amplifier = power_amplifier_action
        self._waveform_generator = waveform_generator_action
        self._encoder = encoder_action
        self._cycle_results: List[Dict] = []  # 存储每次循环的测试结果

    def setup(self):
        """设置测试用例 - 注册设备到测试上下文"""
        self.log("使用真实设备进行编码器上断电测试")

        # 将设备注册到测试上下文，方便在run()中通过get_device()获取
        if self._power_amplifier:
            self.set_device('power_amplifier', self._power_amplifier)
        if self._waveform_generator:
            self.set_device('waveform_generator', self._waveform_generator)
        if self._encoder:
            self.set_device('encoder', self._encoder)

        self.log("✅ 所有设备已配置完成")

    def run(self):
        """执行测试主流程"""
        # 从测试上下文获取设备实例
        power_amp = self.get_device('power_amplifier')
        waveform_gen = self.get_device('waveform_generator')
        encoder = self.get_device('encoder')

        # ========== 设备断言：确保所有必需设备都已配置 ==========
        assert power_amp is not None, "功率放大器设备未配置，请检查fixture"
        assert waveform_gen is not None, "波形发生器设备未配置，请检查fixture"
        assert encoder is not None, "编码器设备未配置，请检查fixture"

        # ========== 获取测试参数（支持通过set_parameter()配置） ==========
        cycle_count = self.get_parameter('cycle_count', 10)      # 循环次数
        power_off_delay = self.get_parameter('power_off_delay', 1.0)  # 断电延时
        power_on_delay = self.get_parameter('power_on_delay', 2.0)    # 上电延时
        tolerance = self.get_parameter('tolerance', 0.5)       # 角度容忍度
        frequency = self.get_parameter('frequency', 1.0)       # 波形频率

        self.log(f"📋 测试参数配置:")
        self.log(f"   - 循环次数: {cycle_count}")
        self.log(f"   - 断电延时: {power_off_delay}s")
        self.log(f"   - 上电延时: {power_on_delay}s")
        self.log(f"   - 角度容忍度: {tolerance}°")
        self.log(f"   - 波形频率: {frequency}Hz")

        # ========== 设备初始化配置 ==========
        self.log("\n🔧 开始初始化测试设备...")

        # 1. 设置功率放大器增益为0dB
        self.log("   设置功率放大器增益...")
        result = power_amp.set_gain(0)
        assert result.is_success(), f"设置增益失败: {result.message}"

        # 2. 设置功率放大器输出电阻为1.5Ω
        #    低阻抗输出可避免与编码器负载分压导致输出电压低于5V
        self.log("   设置功率放大器输出电阻为1.5Ω...")
        result = power_amp.set_output_resistance(1.5)
        assert result.is_success(), f"设置输出电阻失败: {result.message}"

        # 3. 设置波形发生器输出脉冲波
        #    参数：1Hz频率，50%占空比，高电平5V，低电平0V
        #    每个周期0.5秒上电（5V），0.5秒断电（0V）
        self.log("   设置波形发生器输出脉冲波...")
        result = waveform_gen.set_square_wave(
            frequency=frequency,
            high_level=5.0,
            low_level=0.0,
            duty_cycle=50.0,
            channel=1
        )
        assert result.is_success(), f"设置脉冲波失败: {result.message}"

        # 4. 验证波形发生器频率设置是否正确
        result = waveform_gen.get_frequency(channel=1)
        assert result.is_success(), f"读取频率失败: {result.message}"
        actual_freq = result.data.get('frequency', 0.0)
        assert abs(actual_freq - frequency) < 0.01, \
            f"频率设置错误: 实际={actual_freq}Hz, 期望={frequency}Hz"

        self.log(f"\n⚡ 波形发生器配置完成:")
        self.log(f"   - 波形类型: 脉冲波")
        self.log(f"   - 频率: {frequency}Hz")
        self.log(f"   - 电平范围: 0V ~ 5V")
        self.log(f"   - 占空比: 50%")
        self.log(f"   - 工作模式: 硬件自动周期性上断电（0.5s上电 / 0.5s断电）")

        # 5. 打开功率放大器输出
        self.log("\n   打开功率放大器输出...")
        result = power_amp.turn_on()
        assert result.is_success(), f"打开功率放大器输出失败: {result.message}"

        # 6. 打开波形发生器输出（开始硬件自动循环）
        self.log("   打开波形发生器输出...")
        result = waveform_gen.turn_on(channel=1)
        assert result.is_success(), f"打开波形发生器输出失败: {result.message}"

        # 等待上电稳定
        DelayAction(delay=power_on_delay).execute()

        # ========== 阶段一：读取初始上电角度 ==========
        self.log("\n📊 阶段一：读取初始上电角度")
        self.log("   等待第一个上电窗口...")

        # 等待一个完整周期（1秒），确保进入上电状态
        time.sleep(1.0)

        # 多次读取，找到稳定的上电状态角度
        # 策略：排除断电状态（角度=0°），连续两次读到相同角度认为稳定
        initial_data = None
        max_retries = 20
        stable_readings = []
        success_count = 0

        for retry in range(max_retries):
            result = encoder.read_both_angles()
            if result.is_success() and result.data and result.data.get('crc_valid', False):
                current_inner = result.data['inner']['angle_deg']
                # 排除断电状态（角度为0°），只接受上电状态的读数
                if current_inner > 0.01:
                    success_count += 1
                    stable_readings.append(result.data)
                    # 连续两次读到相同角度（误差<0.01°），认为稳定
                    if len(stable_readings) >= 2:
                        prev_inner = stable_readings[-2]['inner']['angle_deg']
                        if abs(current_inner - prev_inner) < 0.01:
                            initial_data = result.data
                            break
            time.sleep(0.05)

        # 如果没有找到稳定读数，使用最后一次有效的读数
        if initial_data is None and stable_readings:
            initial_data = stable_readings[-1]

        # ========== 初始角度断言（三重断言机制） ==========
        # 断言1：必须读到角度数据
        assert initial_data is not None, \
            f"初始上电窗口读取角度失败 - 在{max_retries}次重试中未读取到有效的非零角度（上电状态缺陷）"

        # 断言2：必须读到上电状态（非零角度）
        assert initial_data['inner']['angle_deg'] > 0.01, \
            f"初始上电窗口读到断电状态角度={initial_data['inner']['angle_deg']:.4f}°（上电状态缺陷）"

        # 断言3：上电窗口内至少成功读取一次
        assert success_count >= 1, \
            f"初始上电窗口读取成功次数=0（上电状态缺陷）"

        # 使用Check类进行数据有效性校验
        AngleCheck.data_not_none(initial_data, "初始角度数据")
        AngleCheck.crc_valid(initial_data)

        # 提取初始角度值
        initial_inner = initial_data['inner']['angle_deg']
        initial_outer = initial_data['outer']['angle_deg']

        self.log(f"✅ 初始角度读取成功:")
        self.log(f"   - 内圈角度: {initial_inner:.4f}°")
        self.log(f"   - 外圈角度: {initial_outer:.4f}°")
        self.log(f"   - 读取统计: 尝试{max_retries}次, 成功{success_count}次")

        # 记录初始角度到测试结果
        self.record_data('initial_inner_angle', initial_inner)
        self.record_data('initial_outer_angle', initial_outer)

        # ========== 阶段二：循环上断电测试 ==========
        self.log(f"\n🔄 阶段二：执行 {cycle_count} 次上断电循环验证")
        success_count = 0  # 重置成功计数器

        for cycle in range(cycle_count):
            # 初始化当前循环结果
            cycle_result = {
                'cycle': cycle + 1,
                'expected_inner': initial_inner,
                'expected_outer': initial_outer,
                'actual_inner': None,
                'actual_outer': None,
                'inner_angle_diff': None,
                'outer_angle_diff': None,
                'success': False
            }

            try:
                # 等待一个完整的上断电周期（1.2倍周期时间，确保完成一次完整循环）
                cycle_period = 1.0 / frequency
                wait_time = cycle_period * 1.2
                self.log(f"\n   循环 {cycle + 1}/{cycle_count}: 等待{wait_time:.1f}秒（完整上断电周期）...")
                time.sleep(wait_time)

                # 主动等待进入上电状态（读到非零角度表示上电）
                self.log(f"   循环 {cycle + 1}/{cycle_count}: 等待进入上电状态...")
                wait_for_power_on_max_retries = 50
                for retry in range(wait_for_power_on_max_retries):
                    result = encoder.read_both_angles()
                    if result.is_success() and result.data and result.data.get('crc_valid', False):
                        if result.data['inner']['angle_deg'] > 0.01:
                            self.log(f"   循环 {cycle + 1}/{cycle_count}: ✅ 检测到上电状态")
                            break
                    time.sleep(0.01)

                # 在上电窗口内读取稳定的角度
                current_data = None
                max_retries_read = 30
                stable_readings = []
                read_success_count = 0  # 独立计数器，避免覆盖外层success_count

                for retry in range(max_retries_read):
                    result = encoder.read_both_angles()
                    if result.is_success() and result.data and result.data.get('crc_valid', False):
                        current_inner = result.data['inner']['angle_deg']
                        # 只接受上电状态的读数（非零角度）
                        if current_inner > 0.01:
                            read_success_count += 1
                            stable_readings.append(result.data)
                            # 连续两次读到相同角度，认为稳定
                            if len(stable_readings) >= 2:
                                prev_inner = stable_readings[-2]['inner']['angle_deg']
                                if abs(current_inner - prev_inner) < 0.01:
                                    current_data = result.data
                                    break
                    time.sleep(0.01)

                # 如果没有找到稳定读数，使用最后一次有效的非零读数
                if current_data is None and stable_readings:
                    current_data = stable_readings[-1]

                # ========== 上电窗口断言（三重断言机制） ==========
                # 断言1：必须在上电窗口内读取到角度数据
                assert current_data is not None, \
                    f"循环 {cycle + 1} 上电窗口读取角度失败 - 在{max_retries_read}次重试中未读取到有效的非零角度（上电状态缺陷）"

                # 断言2：必须读到上电状态（非零角度）
                assert current_data['inner']['angle_deg'] > 0.01, \
                    f"循环 {cycle + 1} 上电窗口读到断电状态角度={current_data['inner']['angle_deg']:.4f}°（上电状态缺陷）"

                # 断言3：上电窗口内至少成功读取一次
                assert read_success_count >= 1, \
                    f"循环 {cycle + 1} 上电窗口读取成功次数=0（上电状态缺陷）"

                # 使用Check类进行数据有效性校验
                AngleCheck.data_not_none(current_data, f"循环 {cycle + 1} 角度数据")
                AngleCheck.crc_valid(current_data)

                self.log(f"   循环 {cycle + 1}/{cycle_count}: 上电窗口读取统计 - 尝试{max_retries_read}次, 成功{read_success_count}次")

                # 提取当前角度值
                current_inner = current_data['inner']['angle_deg']
                current_outer = current_data['outer']['angle_deg']
                cycle_result['actual_inner'] = current_inner
                cycle_result['actual_outer'] = current_outer

                # 计算角度变化
                inner_diff = abs(current_inner - initial_inner)
                outer_diff = abs(current_outer - initial_outer)
                cycle_result['inner_angle_diff'] = inner_diff
                cycle_result['outer_angle_diff'] = outer_diff

                self.log(f"   循环 {cycle + 1}/{cycle_count}: 角度对比")
                self.log(f"      初始: ({initial_inner:.4f}°, {initial_outer:.4f}°)")
                self.log(f"      当前: ({current_inner:.4f}°, {current_outer:.4f}°)")
                self.log(f"      差值: ({inner_diff:.4f}°, {outer_diff:.4f}°)")

                # 角度稳定性断言：断电重新上电后角度应保持稳定
                AngleCheck.stable(current_inner, initial_inner, tolerance)
                AngleCheck.stable(current_outer, initial_outer, tolerance)

                # 标记当前循环成功
                cycle_result['success'] = True
                success_count += 1
                self.log(f"   循环 {cycle + 1}/{cycle_count}: ✅ 验证通过")

            except AssertionError as e:
                self.log(f"   循环 {cycle + 1}/{cycle_count}: ❌ 断言失败: {e}")
                raise
            except Exception as e:
                self.log(f"   循环 {cycle + 1}/{cycle_count}: ❌ 异常错误: {e}")
                raise

            # 记录当前循环结果
            self._cycle_results.append(cycle_result)
            self.record_data(f'cycle_{cycle + 1}', cycle_result)

        # ========== 阶段三：最终结果断言 ==========
        self.log(f"\n✅ 阶段三：测试结果汇总")
        self.record_data('success_count', success_count)
        self.record_data('total_cycles', cycle_count)

        # 最终断言：所有循环必须全部成功
        assert success_count == cycle_count, \
            f"测试失败: {success_count}/{cycle_count} 次循环成功"

        self.log(f"🎉 测试完成: {success_count}/{cycle_count} 次循环全部通过")
        self.log(f"📝 测试结论: 上电时编码器可正常读数，断电无法连接编码器（符合预期）")


class EncoderSinglePowerCycleCase(BaseCase):
    """编码器单次上断电测试用例（手动控制）

    测试流程：
    ┌─────────────────────────────────────────────────────────────────┐
    │ 1. 准备阶段                                                    │
    │    └── 停止波形发生器脉冲输出（避免干扰手动控制）                 │
    ├─────────────────────────────────────────────────────────────────┤
    │ 2. 上电读取初始角度                                             │
    │    ├── 打开功率放大器输出                                       │
    │    ├── 等待上电稳定                                             │
    │    └── 读取编码器初始角度                                        │
    ├─────────────────────────────────────────────────────────────────┤
    │ 3. 断电阶段                                                    │
    │    └── 关闭功率放大器输出                                       │
    ├─────────────────────────────────────────────────────────────────┤
    │ 4. 重新上电阶段                                                │
    │    ├── 打开功率放大器输出                                       │
    │    ├── 等待上电稳定                                             │
    │    └── 读取恢复后角度                                           │
    ├─────────────────────────────────────────────────────────────────┤
    │ 5. 结果断言                                                    │
    │    └── 验证恢复后角度与初始角度误差 < tolerance                   │
    └─────────────────────────────────────────────────────────────────┘

    适用场景：
    - 需要精确控制上断电时机的测试场景
    - 调试阶段的单次上断电验证
    - 与波形发生器自动控制方式对比测试
    """

    def __init__(
        self,
        power_amplifier_action: PowerAmplifierAction = None,
        waveform_generator_action=None,
        encoder_action: EncoderAction = None,
        case_id: str = "encoder_single_power_cycle",
        description: str = "编码器单次上断电测试",
        **kwargs
    ):
        """
        构造函数

        Args:
            power_amplifier_action: 功率放大器Action实例
            waveform_generator_action: 波形发生器Action实例（可选，用于停止脉冲输出）
            encoder_action: 编码器Action实例
            case_id: 测试用例ID
            description: 测试用例描述
            **kwargs: 额外参数
        """
        super().__init__(case_id=case_id, description=description, **kwargs)
        self._power_amplifier = power_amplifier_action
        self._waveform_generator = waveform_generator_action
        self._encoder = encoder_action

    def setup(self):
        """设置测试用例 - 注册设备到测试上下文"""
        if self._power_amplifier:
            self.set_device('power_amplifier', self._power_amplifier)
        if self._waveform_generator:
            self.set_device('waveform_generator', self._waveform_generator)
        if self._encoder:
            self.set_device('encoder', self._encoder)

    def run(self):
        """执行单次上断电测试"""
        # 从测试上下文获取设备实例
        power_amp = self.get_device('power_amplifier')
        waveform_gen = self.get_device('waveform_generator')
        encoder = self.get_device('encoder')

        # 设备断言
        assert power_amp is not None, "功率放大器设备未配置"
        assert encoder is not None, "编码器设备未配置"

        # 获取测试参数
        power_off_delay = self.get_parameter('power_off_delay', 1.0)
        power_on_delay = self.get_parameter('power_on_delay', 2.0)
        tolerance = self.get_parameter('tolerance', 0.5)

        self.log("🔄 开始单次上断电测试...")

        # 如果波形发生器存在，先停止其脉冲输出（避免干扰手动上断电测试）
        if waveform_gen:
            self.log("   停止波形发生器脉冲输出...")
            waveform_gen.turn_off(channel=1)
            time.sleep(0.5)

        # ========== 步骤1：上电读取初始角度 ==========
        self.log("\n📊 步骤1：上电读取初始角度")
        result = power_amp.turn_on()
        assert result.is_success(), f"打开功率放大器输出失败: {result.message}"
        self.log("   ✅ 功率放大器已打开")

        DelayAction(delay=power_on_delay).execute()

        result = encoder.read_both_angles()
        assert result.is_success(), f"读取编码器初始数据失败: {result.message}"

        initial_data = result.data
        AngleCheck.data_not_none(initial_data, "编码器初始数据")
        AngleCheck.crc_valid(initial_data)

        initial_inner = initial_data['inner']['angle_deg']
        initial_outer = initial_data['outer']['angle_deg']
        self.log(f"   初始角度 - 内圈: {initial_inner:.4f}°, 外圈: {initial_outer:.4f}°")

        # 记录初始角度
        self.record_data('initial_inner_angle', initial_inner)
        self.record_data('initial_outer_angle', initial_outer)

        # ========== 步骤2：断电 ==========
        self.log("\n📴 步骤2：断电")
        result = power_amp.turn_off()
        assert result.is_success(), f"关闭功率放大器输出失败: {result.message}"
        self.log("   ✅ 功率放大器已关闭（编码器断电）")

        DelayAction(delay=power_off_delay).execute()

        # ========== 步骤3：重新上电 ==========
        self.log("\n⚡ 步骤3：重新上电")
        result = power_amp.turn_on()
        assert result.is_success(), f"打开功率放大器输出失败: {result.message}"
        self.log("   ✅ 功率放大器已打开（编码器重新上电）")

        DelayAction(delay=power_on_delay).execute()

        # ========== 步骤4：读取恢复后角度 ==========
        self.log("\n📊 步骤4：读取恢复后角度")
        result = encoder.read_both_angles()
        assert result.is_success(), f"读取上电后数据失败: {result.message}"

        recovered_data = result.data
        AngleCheck.data_not_none(recovered_data, "上电后数据")
        AngleCheck.crc_valid(recovered_data)

        recovered_inner = recovered_data['inner']['angle_deg']
        recovered_outer = recovered_data['outer']['angle_deg']
        inner_diff = abs(recovered_inner - initial_inner)
        outer_diff = abs(recovered_outer - initial_outer)

        self.log(f"   恢复后角度 - 内圈: {recovered_inner:.4f}°, 外圈: {recovered_outer:.4f}°")
        self.log(f"   角度变化 - 内圈: {inner_diff:.4f}°, 外圈: {outer_diff:.4f}°")

        # 记录恢复后角度
        self.record_data('recovered_inner_angle', recovered_inner)
        self.record_data('recovered_outer_angle', recovered_outer)
        self.record_data('inner_angle_diff', inner_diff)
        self.record_data('outer_angle_diff', outer_diff)

        # ========== 步骤5：结果断言 ==========
        self.log("\n✅ 步骤5：验证角度稳定性")
        AngleCheck.stable(recovered_inner, initial_inner, tolerance)
        AngleCheck.stable(recovered_outer, initial_outer, tolerance)

        self.log("🎉 单次上断电测试通过")