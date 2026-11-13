"""
电源设备规范示例 - 基于测试经验

【经验教训】
1. 寄存器地址偏移256（双路型号）
2. 数据格式：32位整数，不是IEEE 754
3. 单位：电压mV，电流mA
4. 输出控制逻辑：0=打开，1=关闭（与常规相反）
5. CC/CV状态逻辑：1=CV，0=CC（与常规相反）
"""

POWER_SUPPLY_SPEC = {
    "device_name": "power_supply",
    "class_name": "PowerSupply",
    "description": "可编程双路电源设备（Modbus RTU）",
    
    "manufacturer": "博瑞",
    "model": "程控系列双路输出",
    "protocol": "modbus_rtu",
    "communication": "rs485",
    "channels": 2,
    
    # 设备配置（关键经验）
    "device_config": {
        "channels": 2,
        "address_offset": 256,  # 双路型号地址偏移
        "byte_order": "big",    # 大端序
        "data_format": "uint32" # 32位整数格式
    },
    
    # 通用寄存器
    "registers": {
        "REMOTE_MODE": 0x0000  # 远程/本地模式 (0=本地, 1=远程)
    },
    
    # 通道寄存器映射（关键经验）
    "channel_registers": {
        1: {
            # 电压设置（32位整数，单位mV）
            "V_SET": {
                "address": 0x0001,  # 原始地址（会自动加上address_offset）
                "format": "uint32",
                "unit": "mV",
                "scale": 0.001,    # mV → V
                "description": "通道1设定电压"
            },
            # 电流设置（32位整数，单位mA）
            "I_SET": {
                "address": 0x0003,
                "format": "uint32",
                "unit": "mA",
                "scale": 0.001,    # mA → A
                "description": "通道1设定电流"
            },
            # 输出电压（32位整数，单位mV）
            "V_OUT": {
                "address": 0x0005,
                "format": "uint32",
                "unit": "mV",
                "scale": 0.001,    # mV → V
                "description": "通道1实际输出电压"
            },
            # 输出电流（32位整数，单位mA）
            "I_OUT": {
                "address": 0x0007,
                "format": "uint32",
                "unit": "mA",
                "scale": 0.001,    # mA → A
                "description": "通道1实际输出电流"
            },
            # 输出控制（关键经验：逻辑相反）
            "OUTPUT": {
                "address": 0x0009,
                "format": "uint16",
                "control_logic": {
                    "on": 0,   # 0=打开（与常规相反）
                    "off": 1   # 1=关闭（与常规相反）
                },
                "description": "通道1输出控制"
            },
            # CC/CV状态（关键经验：逻辑相反）
            "STATUS": {
                "address": 0x000A,
                "format": "uint16",
                "control_logic": {
                    "cv": 1,   # 1=CV（与常规相反）
                    "cc": 0    # 0=CC（与常规相反）
                },
                "description": "通道1CC/CV状态"
            }
        },
        2: {
            # 通道2寄存器（地址偏移）
            "V_SET": {
                "address": 0x000B,
                "format": "uint32",
                "unit": "mV",
                "scale": 0.001,
                "description": "通道2设定电压"
            },
            "I_SET": {
                "address": 0x000D,
                "format": "uint32",
                "unit": "mA",
                "scale": 0.001,
                "description": "通道2设定电流"
            },
            "V_OUT": {
                "address": 0x000F,
                "format": "uint32",
                "unit": "mV",
                "scale": 0.001,
                "description": "通道2实际输出电压"
            },
            "I_OUT": {
                "address": 0x0011,
                "format": "uint32",
                "unit": "mA",
                "scale": 0.001,
                "description": "通道2实际输出电流"
            },
            "OUTPUT": {
                "address": 0x0013,
                "format": "uint16",
                "control_logic": {
                    "on": 0,
                    "off": 1
                },
                "description": "通道2输出控制"
            },
            "STATUS": {
                "address": 0x0014,
                "format": "uint16",
                "control_logic": {
                    "cv": 1,
                    "cc": 0
                },
                "description": "通道2CC/CV状态"
            }
        }
    },
    
    # 数据格式配置
    "data_formats": {
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
        },
        "status": {
            "normal": {"cv": 0, "cc": 1},
            "inverted": {"cv": 1, "cc": 0}
        }
    },
    
    # 设备参数
    "parameters": {
        "max_voltage": 30.0,
        "max_current": 5.0,
        "voltage_precision": 0.001,
        "current_precision": 0.001
    },
    
    # 初始化命令
    "init_commands": [],
    
    # 远程模式寄存器
    "remote_mode_register": "REMOTE_MODE",
    
    # 自定义方法
    "methods": [
        {
            "name": "set_voltage",
            "description": "设置通道电压",
            "parameters": [
                {
                    "name": "voltage",
                    "type": "float",
                    "description": "目标电压值(V)"
                },
                {
                    "name": "channel",
                    "type": "int",
                    "default": 1,
                    "description": "通道号(1或2)"
                }
            ],
            "return_type": "bool",
            "return_description": "是否设置成功"
        },
        {
            "name": "set_current",
            "description": "设置通道电流",
            "parameters": [
                {
                    "name": "current",
                    "type": "float",
                    "description": "目标电流值(A)"
                },
                {
                    "name": "channel",
                    "type": "int",
                    "default": 1,
                    "description": "通道号(1或2)"
                }
            ],
            "return_type": "bool",
            "return_description": "是否设置成功"
        },
        {
            "name": "turn_on",
            "description": "打开通道输出",
            "parameters": [
                {
                    "name": "channel",
                    "type": "int",
                    "default": 1,
                    "description": "通道号(1或2)"
                }
            ],
            "return_type": "bool",
            "return_description": "是否打开成功"
        },
        {
            "name": "turn_off",
            "description": "关闭通道输出",
            "parameters": [
                {
                    "name": "channel",
                    "type": "int",
                    "default": 1,
                    "description": "通道号(1或2)"
                }
            ],
            "return_type": "bool",
            "return_description": "是否关闭成功"
        },
        {
            "name": "read_voltage",
            "description": "读取实际输出电压",
            "parameters": [
                {
                    "name": "channel",
                    "type": "int",
                    "default": 1,
                    "description": "通道号(1或2)"
                }
            ],
            "return_type": "float",
            "return_description": "实际输出电压(V)"
        },
        {
            "name": "read_current",
            "description": "读取实际输出电流",
            "parameters": [
                {
                    "name": "channel",
                    "type": "int",
                    "default": 1,
                    "description": "通道号(1或2)"
                }
            ],
            "return_type": "float",
            "return_description": "实际输出电流(A)"
        }
    ]
}

# 使用示例
if __name__ == '__main__':
    import json
    print("电源设备规范示例：")
    print(json.dumps(POWER_SUPPLY_SPEC, indent=2, ensure_ascii=False))