"""
检查pymodbus API
"""
from pymodbus.client import ModbusSerialClient
import inspect

# 创建客户端
client = ModbusSerialClient(port='COM4')

# 检查write_register方法的签名
print("write_register 方法签名:")
print(inspect.signature(client.write_register))

# 检查write_registers方法的签名
print("\nwrite_registers 方法签名:")
print(inspect.signature(client.write_registers))

# 检查read_holding_registers方法的签名
print("\nread_holding_registers 方法签名:")
print(inspect.signature(client.read_holding_registers))

# 检查客户端的属性
print("\n客户端属性:")
print([attr for attr in dir(client) if not attr.startswith('_')])