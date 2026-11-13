"""
Flow 层 pytest 测试 - 使用完整 pytest 特性
"""
import pytest
from projects.encoder_test.actions.flow import StartupFlow, ShutdownFlow, SequenceFlow, CalibrationFlow
from actions import DelayAction, PowerOnAction, PowerOffAction


@pytest.mark.flow
class TestStartupFlow:
    """开机流程测试"""
    
    @pytest.mark.parametrize("voltage,current", [
        (3.3, 0.5),
        (5.0, 1.0),
    ])
    def test_startup_flow(self, power_supply, voltage, current):
        """参数化测试 - 不同电压开机"""
        flow = StartupFlow(
            power=power_supply,
            motor=None,
            encoder=None,
            voltage=voltage,
            current=current
        )
        result = flow.execute()
        assert result.success is True
        assert result.state == "success"
    
    def test_startup_flow_full(self, power_supply, motor, encoder):
        """测试完整开机流程"""
        flow = StartupFlow(
            power=power_supply,
            motor=motor,
            encoder=encoder,
            voltage=5.0,
            current=1.0
        )
        result = flow.execute()
        assert result.success is True
        assert len(result.action_results) >= 2


@pytest.mark.flow
class TestShutdownFlow:
    """关机流程测试"""
    
    def test_shutdown_flow(self, power_supply):
        """测试关机流程"""
        power_supply.connect()
        flow = ShutdownFlow(power=power_supply, motor=None)
        result = flow.execute()
        assert result.success is True
    
    def test_shutdown_with_motor(self, power_supply, motor):
        """测试带电机关机"""
        power_supply.connect()
        motor.connect()
        flow = ShutdownFlow(power=power_supply, motor=motor)
        result = flow.execute()
        assert result.success is True


@pytest.mark.flow
class TestSequenceFlow:
    """序列流程测试"""
    
    def test_sequence_flow(self, power_supply):
        """测试序列流程"""
        flow = SequenceFlow(flow_id="test_sequence")
        flow.add(PowerOnAction(power=power_supply, voltage=5.0))
        flow.add(DelayAction(delay=0.2))
        flow.add(PowerOffAction(power=power_supply))
        
        result = flow.execute()
        
        assert result.success is True
        assert len(result.action_results) == 3
        
        for ar in result.action_results:
            assert ar['success'] is True
    
    def test_sequence_flow_empty(self):
        """测试空序列流程"""
        flow = SequenceFlow(flow_id="empty_flow")
        result = flow.execute()
        assert result.success is True
        assert len(result.action_results) == 0
    
    @pytest.mark.parametrize("delay_count,delay", [
        (3, 0.1),
        (5, 0.2),
    ])
    def test_sequence_flow_multiple_delays(self, delay_count, delay):
        """参数化测试 - 多延时序列"""
        from drivers.mock.mock_modbus import MockModbusDriver
        from drivers.factory import DeviceFactory
        
        mock = MockModbusDriver()
        ps = DeviceFactory.create('power_supply', protocol=mock, driver_id='ps1')
        
        flow = SequenceFlow(flow_id="multi_delay")
        flow.add(PowerOnAction(power=ps, voltage=5.0))
        
        for _ in range(delay_count):
            flow.add(DelayAction(delay=delay))
        
        flow.add(PowerOffAction(power=ps))
        
        result = flow.execute()
        assert result.success is True


@pytest.mark.flow
class TestCalibrationFlow:
    """标定流程测试"""
    
    def test_calibration_flow(self, encoder):
        """测试标定流程"""
        flow = CalibrationFlow(
            encoder=encoder,
            power=None,
            motor=None
        )
        result = flow.execute()
        assert result.success is True


@pytest.mark.flow
class TestFlowState:
    """流程状态测试"""
    
    def test_flow_initial_state(self):
        """测试流程初始状态"""
        flow = SequenceFlow(flow_id="state_test")
        assert flow.state == "idle"
    
    def test_flow_state_transitions(self, power_supply):
        """测试流程状态转换"""
        flow = SequenceFlow(flow_id="transitions")
        flow.add(PowerOnAction(power=power_supply, voltage=5.0))
        
        assert flow.state == "idle"
        result = flow.execute()
        assert flow.state == "success"