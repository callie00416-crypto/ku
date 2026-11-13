"""
检查Modbus客户端属性
"""
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(port='COM4', baudrate=9600)
client.connect()

print("客户端属性:")
print(f"connected: {client.connected}")
print(f"is_socket_open: {client.is_socket_open()}")
print(f"所有属性: {[attr for attr in dir(client) if not attr.startswith('_')]}")

client.close()