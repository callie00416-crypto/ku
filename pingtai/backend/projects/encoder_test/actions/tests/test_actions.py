"""
Action 层 pytest 测试 - 使用完整 pytest 特性
"""
import pytest
from actions import (
    PowerOnAction, PowerOffAction, PowerStableAction,
    DelayAction, SafetyCheckAction, MotorHomeAction,
)


@pytest.mark.action
class TestPowerAction:
    """电源动作测试"""
    
    @pytest.mark.parametrize("voltage,current", [
        (3.3, 0.5),
        (5.0, 1.0),
        (12.0, 2.0),
    ])
    def test_power_on_action(self, power_supply, voltage, current):
        """参数化测试 - 不同电压上电"""
        action = PowerOnAction(
            power=power_supply,
            voltage=voltage,
            current=current,
            channel=1
        )
        result = action.execute()
        assert result.is_success() is True
        assert power_supply.is_connected() is True
    
    def test_power_off_action(self, power_supply):
        """测试电源下电动作"""
        power_supply.connect()
        action = PowerOffAction(power=power_supply, channel=1)
        result = action.execute()
        assert result.is_success() is True
    
    @pytest.mark.parametrize("stable_time,tolerance", [
        (0.5, 0.2),
        (1.0, 0.1),
    ])
    def test_power_stable_action(self, power_supply, stable_time, tolerance):
        """参数化测试 - 电源稳定等待"""
        power_supply.connect()
        action = PowerStableAction(
            power=power_supply,
            channel=1,
            stable_time=stable_time,
            tolerance=tolerance
        )
        result = action.execute()
        assert result.is_success() is True


@pytest.mark.action
class TestCommonAction:
    """通用动作测试"""
    
    @pytest.mark.parametrize("delay", [0.1, 0.2, 0.5])
    def test_delay_action(self, delay):
        """参数化测试 - 不同时长延时"""
        action = DelayAction(delay=delay)
        result = action.execute()
        assert result.is_success() is True
        assert result.data['delay'] == delay
    
    def test_safety_check_action(self, devices):
        """测试安全检查动作"""
        action = SafetyCheckAction(devices=devices)
        result = action.execute()
        assert result.is_success() is True
    
    def test_safety_check_no_devices(self):
        """测试无设备安全检查"""
        action = SafetyCheckAction(devices={})
        result = action.execute()
        assert result.is_success() is True


@pytest.mark.action
class TestMotorAction:
    """电机动作测试"""
    
    def test_motor_home_action(self, motor):
        """测试电机回零动作"""
        motor.connect()
        action = MotorHomeAction(motor=motor)
        result = action.execute()
        assert result.is_success() is True


@pytest.mark.action
class TestActionLifecycle:
    """Action 生命周期测试"""
    
    def test_action_execute_calls_lifecycle(self, power_supply):
        """测试动作执行调用完整生命周期"""
        before_called = []
        after_called = []
        
        class InstrumentedAction(PowerOnAction):
            def before_run(self):
                before_called.append(True)
                super().before_run()
            
            def after_run(self):
                after_called.append(True)
                super().after_run()
        
        action = InstrumentedAction(power=power_supply, voltage=5.0)
        result = action.execute()
        
        assert len(before_called) == 1
        assert len(after_called) == 1
        assert result.is_success() is True


@pytest.mark.flow
class TestActionFlow:
    """动作流程测试"""
    
    def test_action_sequence_flow(self, power_supply):
        """测试动作序列流程"""
        from actions.flow import SequenceFlow
        
        flow = SequenceFlow(flow_id="test_flow")
        flow.add(PowerOnAction(power=power_supply, voltage=5.0))
        flow.add(DelayAction(delay=0.2))
        flow.add(PowerOffAction(power=power_supply))
        
        result = flow.execute()
        
        assert result.success is True
        assert len(result.action_results) == 3
    
    def test_action_flow_empty(self):
        """测试空动作流程"""
        from actions.flow import SequenceFlow
        
        flow = SequenceFlow(flow_id="empty_flow")
        result = flow.execute()
        assert result.success is True