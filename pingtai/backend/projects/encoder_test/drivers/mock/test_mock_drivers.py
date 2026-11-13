"""
Mock 驱动测试脚本

验证所有 Mock 驱动的基本功能是否正常工作
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from projects.encoder_test.drivers.mock import MockSerial, MockCAN, MockModbusDriver, MockEncoder, MockMotor


def test_mock_serial():
    """测试 MockSerial"""
    print("=== 测试 MockSerial ===")
    
    serial = MockSerial('test_serial', port='COM1', baudrate=9600)
    
    assert serial.open()
    assert serial.is_open
    
    # 测试发送
    data = b'\x01\x02\x03'
    result = serial.send(data)
    assert result == len(data)
    assert serial.get_send_buffer() == data
    
    # 测试自动响应
    serial.set_auto_response(b'\x04\x05\x06')
    response = serial.recv(timeout=1.0)
    assert response == b'\x04\x05\x06'
    
    # 测试队列响应
    serial.clear_buffers()
    serial.queue_response(b'\x07\x08\x09')
    response = serial.recv(timeout=1.0)
    assert response == b'\x07\x08\x09'
    
    serial.close()
    assert not serial.is_open
    
    print("✓ MockSerial 测试通过\n")


def test_mock_can():
    """测试 MockCAN"""
    print("=== 测试 MockCAN ===")
    
    can = MockCAN('test_can', channel='can0', bitrate=500000)
    
    assert can.connect()
    assert can.is_open
    
    # 测试发送/接收
    data = b'\x11\x22\x33\x44'
    result = can.send(data)
    assert result == len(data)
    
    # 发送的数据会被添加到队列（模拟总线回显）
    echo_data = can.recv(timeout=1.0)
    assert echo_data == data
    
    can.queue_message(b'\x55\x66\x77\x88')
    response = can.recv(timeout=1.0)
    assert response == b'\x55\x66\x77\x88'
    
    # 测试错误模式
    can.set_mode('bus_error')
    try:
        can.send(data)
        assert False, "应该抛出异常"
    except RuntimeError:
        pass
    
    can.set_mode('normal')
    can.disconnect()
    assert not can.is_open
    
    print("✓ MockCAN 测试通过\n")


def test_mock_modbus():
    """测试 MockModbusDriver"""
    print("=== 测试 MockModbusDriver ===")
    
    modbus = MockModbusDriver('test_modbus', slave_id=1)
    
    assert modbus.connect()
    assert modbus.is_connected()
    
    # 测试寄存器读写
    modbus.write_register(0x100, 12345)
    assert modbus.read_register(0x100) == 12345
    
    # 测试多个寄存器读写
    modbus.write_registers(0x200, [1, 2, 3])
    assert modbus.read_registers(0x200, 3) == [1, 2, 3]
    
    # 测试 32 位数据
    modbus.write_long(0x300, 0x12345678)
    assert modbus.read_long(0x300) == 0x12345678
    
    # 测试预设值
    modbus.set_register(0x400, 999)
    assert modbus.read_register(0x400) == 999
    
    modbus.disconnect()
    assert not modbus.is_connected()
    
    print("✓ MockModbusDriver 测试通过\n")


def test_mock_encoder():
    """测试 MockEncoder"""
    print("=== 测试 MockEncoder ===")
    
    encoder = MockEncoder('test_encoder', resolution=4096)
    
    assert encoder.connect()
    assert encoder.is_connected()
    
    # 测试角度设置和读取
    encoder.set_angle(45.0)
    data = encoder.read_data()
    assert abs(data['angle'] - 45.0) < 0.01
    
    # 测试速度设置
    encoder.set_speed(10.0)
    data = encoder.read_data()
    assert data['speed'] == 10.0
    
    # 测试噪声模式
    encoder.set_noise_level(0.5)
    encoder.mode = 'noisy'
    encoder.set_angle(0.0)
    data = encoder.read_data()
    assert abs(data['angle']) <= 0.5
    
    # 测试重置
    encoder.reset()
    encoder.mode = 'normal'  # 重置后恢复正常模式
    data = encoder.read_data()
    assert data['angle'] == 0.0
    assert data['speed'] == 0.0
    
    encoder.disconnect()
    assert not encoder.is_connected()
    
    print("✓ MockEncoder 测试通过\n")


def test_mock_motor():
    """测试 MockMotor"""
    print("=== 测试 MockMotor ===")
    
    motor = MockMotor('test_motor', position_limit=360.0, max_speed=180.0)
    
    assert motor.connect()
    assert motor.is_connected()
    
    # 测试启动和停止
    motor.start()
    assert motor.running
    
    motor.stop()
    assert not motor.running
    
    # 测试位置移动
    motor.move_to(90.0)
    assert abs(motor.position - 90.0) < 0.01
    
    # 测试相对移动
    motor.move_by(45.0)
    assert abs(motor.position - 135.0) < 0.01
    
    # 测试限位
    motor.move_to(500.0)  # 超过限制
    assert motor.position == 360.0
    assert motor._right_limit
    
    # 测试回零
    motor.start_homing()
    assert motor.position == 0.0
    assert not motor._right_limit
    
    # 测试重置
    motor.reset()
    assert motor.position == 0.0
    assert motor.speed == 0.0
    assert not motor.running
    
    motor.disconnect()
    assert not motor.is_connected()
    
    print("✓ MockMotor 测试通过\n")


if __name__ == '__main__':
    test_mock_serial()
    test_mock_can()
    test_mock_modbus()
    test_mock_encoder()
    test_mock_motor()
    print("=== 所有 Mock 驱动测试通过 ===")