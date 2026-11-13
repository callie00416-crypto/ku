"""
通用设备规范模板

【设计目标】
- 支持多种协议（SCPI、Modbus RTU、Modbus TCP等）
- 支持多种通信方式（USB、RS485、TCP等）
- 统一的规范格式
- 可扩展的配置结构

【协议支持】
1. SCPI - 标准命令可编程仪器协议
2. Modbus RTU - 串口Modbus
3. Modbus TCP - 网络Modbus
4. 自定义协议 - 通过命令模板实现
"""

GENERIC_DEVICE_SPEC_TEMPLATE = {
    # ==================== 基本信息 ====================
    "device_name": "device_name",           # 设备名称（用于文件名）
    "class_name": "DeviceClass",            # 类名（PascalCase）
    "description": "设备描述",              # 设备描述
    
    # ==================== 设备信息 ====================
    "manufacturer": "制造商",               # 制造商
    "model": "型号",                        # 型号
    "serial_number": "",                    # 序列号（可选）
    "firmware_version": "",                 # 固件版本（可选）
    
    # ==================== 协议配置 ====================
    "protocol": {
        "type": "scpi",                     # 协议类型: scpi, modbus_rtu, modbus_tcp, custom
        "version": "",                      # 协议版本（可选）
        "description": "协议描述",          # 协议描述
    },
    
    # ==================== 通信配置 ====================
    "communication": {
        "type": "usb_visa",                 # 通信类型: usb_visa, rs485, tcp, serial, ethernet
        "description": "通信方式描述",      # 通信方式描述
        "config": {                         # 通信特定配置
            # USB VISA配置
            "resource_string": "",          # VISA资源字符串
            "vid": 0x0000,                  # USB Vendor ID
            "pid": 0x0000,                  # USB Product ID
            "timeout": 10000,               # 超时时间(ms)
            
            # RS485配置
            "port": "COM1",                 # 串口
            "baudrate": 9600,               # 波特率
            "bytesize": 8,                  # 数据位
            "parity": "N",                  # 校验位
            "stopbits": 1,                  # 停止位
            
            # TCP配置
            "host": "192.168.0.1",          # IP地址
            "port": 5025,                   # 端口号
        }
    },
    
    # ==================== 通道配置 ====================
    "channels": 1,                          # 通道数量
    "channel_prefix": "CH",                # 通道前缀（可选）
    
    # ==================== SCPI协议配置 ====================
    "scpi_config": {
        # 设备级命令
        "device_commands": {
            "get_id": "*IDN?",              # 获取设备ID
            "reset": "*RST",                # 重置设备
            "clear": "*CLS",                # 清除错误
            "get_error": "SYST:ERR?",       # 获取错误
            "get_options": "*OPT?"          # 获取选项
        },
        
        # 通道命令模板
        # 支持占位符: {channel} - 通道号
        "channel_commands": {
            # 波形设置
            "waveform": {
                "set": ":SOUR{channel}:FUNC {waveform}",
                "get": ":SOUR{channel}:FUNC?",
                "description": "波形类型"
            },
            
            # 频率设置
            "frequency": {
                "set": ":SOUR{channel}:FREQ {frequency}",
                "get": ":SOUR{channel}:FREQ?",
                "description": "频率",
                "unit": "Hz"
            },
            
            # 幅度设置
            "amplitude": {
                "set": ":SOUR{channel}:VOLT {amplitude}",
                "get": ":SOUR{channel}:VOLT?",
                "description": "幅度",
                "unit": "Vpp"
            },
            
            # 偏置设置
            "offset": {
                "set": ":SOUR{channel}:VOLT:OFFS {offset}",
                "get": ":SOUR{channel}:VOLT:OFFS?",
                "description": "偏置",
                "unit": "V"
            },
            
            # 相位设置
            "phase": {
                "set": ":SOUR{channel}:PHAS {phase}",
                "get": ":SOUR{channel}:PHAS?",
                "description": "相位",
                "unit": "deg"
            },
            
            # 输出控制
            "output": {
                "on": ":OUTP{channel} ON",
                "off": ":OUTP{channel} OFF",
                "get": ":OUTP{channel}?",
                "description": "输出控制"
            }
        },
        
        # 响应解析器
        "response_parser": {
            "default": "strip",              # 默认解析: strip, int, float, json, custom
            "custom_parser": ""              # 自定义解析函数（可选）
        },
        
        # 波形类型映射
        "waveforms": {
            "SIN": "正弦波",
            "SQU": "方波",
            "TRI": "三角波",
            "RAMP": "锯齿波",
            "PULS": "脉冲波",
            "NOIS": "噪声",
            "PRBS": "伪随机序列",
            "ARB": "任意波"
        }
    },
    
    # ==================== Modbus协议配置 ====================
    "modbus_config": {
        "slave_id": 1,                      # 从站ID
        "byte_order": "big",                # 字节序: big, little
        
        # 设备配置
        "device_config": {
            "address_offset": 0,             # 地址偏移
            "data_format": "uint16"          # 默认数据格式
        },
        
        # 通用寄存器
        "registers": {
            "REMOTE_MODE": {
                "address": 0x0000,
                "format": "uint16",
                "description": "远程/本地模式"
            }
        },
        
        # 通道寄存器映射
        "channel_registers": {
            1: {
                "V_SET": {
                    "address": 0x0001,
                    "format": "uint32",
                    "unit": "mV",
                    "scale": 0.001,
                    "description": "设定电压"
                },
                "OUTPUT": {
                    "address": 0x0009,
                    "format": "uint16",
                    "control_logic": {
                        "on": 1,
                        "off": 0
                    },
                    "description": "输出控制"
                }
            }
        },
        
        # 数据格式配置
        "data_formats": {
            "uint16": {
                "size": 2,
                "signed": False,
                "description": "16位无符号整数"
            },
            "uint32": {
                "size": 4,
                "signed": False,
                "description": "32位无符号整数"
            },
            "int32": {
                "size": 4,
                "signed": True,
                "description": "32位有符号整数"
            },
            "float32": {
                "size": 4,
                "ieee754": True,
                "description": "IEEE 754浮点数"
            }
        },
        
        # 控制逻辑映射
        "control_logic": {
            "output": {
                "normal": {"on": 1, "off": 0},
                "inverted": {"on": 0, "off": 1}
            }
        }
    },
    
    # ==================== 参数范围 ====================
    "parameters": {
        "frequency": {
            "min": 1,
            "max": 60000000,
            "unit": "Hz",
            "precision": 0.001,
            "description": "频率"
        },
        "amplitude": {
            "min": 0.01,
            "max": 10,
            "unit": "Vpp",
            "precision": 0.01,
            "description": "幅度"
        },
        "offset": {
            "min": -5,
            "max": 5,
            "unit": "V",
            "precision": 0.01,
            "description": "偏置"
        },
        "phase": {
            "min": 0,
            "max": 360,
            "unit": "deg",
            "precision": 0.1,
            "description": "相位"
        }
    },
    
    # ==================== 初始化命令 ====================
    "init_commands": [],                    # 初始化命令列表
    
    # ==================== 自定义方法 ====================
    "methods": [
        {
            "name": "connect",
            "description": "连接设备",
            "parameters": [],
            "return_type": "bool",
            "return_description": "是否连接成功"
        },
        {
            "name": "disconnect",
            "description": "断开设备",
            "parameters": [],
            "return_type": "None",
            "return_description": "无返回值"
        },
        {
            "name": "health_check",
            "description": "健康检查",
            "parameters": [],
            "return_type": "Dict[str, Any]",
            "return_description": "健康状态字典"
        }
    ],
    
    # ==================== 事件配置 ====================
    "events": {
        "on_connect": "device_connected",    # 连接事件
        "on_disconnect": "device_disconnected",  # 断开事件
        "on_error": "device_error",          # 错误事件
        "on_operation_success": "operation_success",  # 操作成功
        "on_operation_failure": "operation_failure"   # 操作失败
    },
    
    # ==================== 其他配置 ====================
    "metadata": {
        "author": "",
        "version": "1.0.0",
        "created": "",
        "modified": "",
        "notes": ""
    }
}

# 协议类型枚举
PROTOCOL_TYPES = {
    "scpi": "标准命令可编程仪器协议",
    "modbus_rtu": "Modbus RTU协议",
    "modbus_tcp": "Modbus TCP协议",
    "custom": "自定义协议"
}

# 通信类型枚举
COMMUNICATION_TYPES = {
    "usb_visa": "USB VISA通信",
    "rs485": "RS485串口通信",
    "tcp": "TCP网络通信",
    "serial": "串口通信",
    "ethernet": "以太网通信"
}

# 数据格式枚举
DATA_FORMATS = {
    "uint16": "16位无符号整数",
    "uint32": "32位无符号整数",
    "int16": "16位有符号整数",
    "int32": "32位有符号整数",
    "float32": "IEEE 754浮点数",
    "float64": "IEEE 754双精度浮点数",
    "string": "字符串",
    "boolean": "布尔值"
}

# 使用示例
if __name__ == '__main__':
    import json
    
    print("=" * 70)
    print("通用设备规范模板")
    print("=" * 70)
    
    print("\n支持的协议类型:")
    for key, value in PROTOCOL_TYPES.items():
        print(f"  - {key}: {value}")
    
    print("\n支持的通信类型:")
    for key, value in COMMUNICATION_TYPES.items():
        print(f"  - {key}: {value}")
    
    print("\n支持的数据格式:")
    for key, value in DATA_FORMATS.items():
        print(f"  - {key}: {value}")
    
    print("\n" + "=" * 70)
    print("完整规范模板:")
    print("=" * 70)
    print(json.dumps(GENERIC_DEVICE_SPEC_TEMPLATE, indent=2, ensure_ascii=False))