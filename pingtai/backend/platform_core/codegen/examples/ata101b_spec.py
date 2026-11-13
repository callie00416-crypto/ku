"""
ATA-101B 功率放大器设备规范

【设备信息】
- 型号: ATA-101B
- 制造商: 安泰电子
- 类型: 功率放大器
- 通道: 单通道
- 带宽: DC~1MHz
- 最大输出电压: 25Vp-p (±12.5Vp)
- 最大输出电流: 2Ap
- 最大输出功率: 25Wp

【通信参数】
- 接口: RS485
- 波特率: 9600
- 数据位: 8
- 停止位: 1
- 校验位: 无
- 流控制: 无
- 编码: ASCII

【协议类型】
- 自定义ASCII协议
- 指令格式: ATATATA,SET,<CMD>,<VALUE>;
- 响应格式: ASCII字符串

【指令集】
1. 输出开: ATA,SET,AON,0000;
2. 输出关: ATA,SET,AOF,0000;
3. 保存设置: ATA,SET,SAV,0000;
4. 输入电阻设置: ATA,SET,RIN,<VALUE>;
   - 0050 = 50Ω
   - 1000 = 1MΩ
5. 输出电阻设置: ATA,SET,ROT,<VALUE>;
   - 0015 = 1.5Ω
   - 0500 = 50Ω
6. 增益设置: ATA,SET,AMP,<VALUE>;
   - 0000 = 0dB
   - 0012 = 12dB
   - 0020 = 20dB

【响应】
- 设置成功: SET DONE!
- 设置越界: OVER RARANGE ERROR!
- 设置指令错误: SET ERROR!
"""
ATA101B_SPEC = {
    "device_name": "power_amplifier",
    "class_name": "ATA101BPowerAmplifier",
    "description": "ATA-101B单通道功率放大器",
    
    "manufacturer": "安泰电子",
    "model": "ATA-101B",
    "serial_number": "",
    "firmware_version": "",
    
    "protocol": {
        "type": "custom",
        "version": "1.0",
        "description": "自定义ASCII协议",
        "encoding": "ASCII"
    },
    
    "communication": {
        "type": "rs485",
        "description": "RS485串口通信",
        "config": {
            "port": "COM1",
            "baudrate": 9600,
            "data_bits": 8,
            "stop_bits": 1,
            "parity": "none",
            "flow_control": "none",
            "timeout": 1000
        }
    },
    
    "channels": 1,
    "channel_prefix": "CH",
    
    "custom_protocol_config": {
        "command_prefix": "ATA,SET,",
        "command_suffix": ";",
        "response_success": "SET DONE!",
        "response_error": "SET ERROR!",
        "response_over_range": "OVER RARANGE ERROR!",
        
        "commands": {
            "output_on": {
                "set": "AON,0000",
                "description": "打开输出"
            },
            "output_off": {
                "set": "AOF,0000",
                "description": "关闭输出"
            },
            "save_settings": {
                "set": "SAVAV,V,0000",
                "description": "保存设置"
            },
            "input_resistance": {
                "set": "RIN,{value}",
                "description": "设置输入电阻",
                "unit": "Ω",
                "value_format": "{value:04d}",
                "value_mapping": {
                    "50": "0050",
                    "1000": "1000"
                }
            },
            "output_resistance": {
                "set": "ROT,{value}",
                "description": "设置输出电阻",
                "unit": "Ω",
                "value_format": "{value:04d}",
                "value_mapping": {
                    "1.5": "0015",
                    "50": "0500"
                }
            },
            "gain": {
                "set": "AMP,{value}",
                "description": "设置增益",
                "unit": "dB",
                "value_format": "{value:04d}",
                "value_mapping": {
                    "0": "0000",
                    "12": "0012",
                    "20": "0020"
                }
            }
        }
    },
    
    "parameters": {
        "input_resistance": {
            "type": "float",
            "unit": "Ω",
            "min": 50.0,
            "max": 1000.0,
            "default": 50.0,
            "description": "输入电阻"
        },
        "output_resistance": {
            "type": "float",
            "unit": "Ω",
            "min": 1.5,
            "max": 50.0,
            "default": 50.0,
            "description": "输出电阻"
        },
        "gain": {
            "type": "int",
            "unit": "dB",
            "min": 0,
            "max": 20,
            "step": 2,
            "default": 0,
            "description": "增益"
        },
        "output_enabled": {
            "type": "bool",
            "default": False,
            "description": "输出使能"
        }
    },
    
    "methods": [
        {
            "name": "output_on",
            "description": "打开输出",
            "parameters": [],
            "return_type": "bool"
        },
        {
            "name": "output_off",
            "description": "关闭输出",
            "parameters": [],
            "return_type": "bool"
        },
        {
            "name": "save_settings",
            "description": "保存设置",
            "parameters": [],
            "return_type": "bool"
        },
        {
            "name": "set_input_resistance",
            "description": "设置输入电阻",
            "parameters": [
                {
                    "name": "resistance",
                    "type": "float",
                    "description": "输入电阻值 (50Ω 或 1000Ω)"
                }
            ],
            "return_type": "bool"
        },
        {
            "name": "set_output_resistance",
            "description": "设置输出电阻",
            "parameters": [
                {
                    "name": "resistance",
                    "type": "float",
                    "description": "输出电阻值 (1.5Ω 或 50Ω)"
                }
            ],
            "return_type": "bool"
        },
        {
            "name": "set_gain",
            "description": "设置增益",
            "parameters": [
                {
                    "name": "gain_db",
                    "type": "int",
                    "description": "增益值 (0-20dB, 步进2dB)"
                }
            ],
            "return_type": "bool"
        },
        {
            "name": "get_status",
            "description": "获取设备状态",
            "parameters": [],
            "return_type": "Dict[str, Any]"
        }
    ],
    
    "init_commands": [],
    
    "device_info": {
        "bandwidth": "DC~1MHz",
        "max_output_voltage": "25Vp-p (±12.5Vp)",
        "max_output_current": "2Ap",
        "max_output_power": "25Wp",
        "output_interface": "BNC",
        "display": "LCD液晶面板"
    }
}


if __name__ == "__main__":
    import json
    
    print("ATA-101B 功率放大器设备规范")
    print("=" * 70)
    print(json.dumps(ATA101B_SPEC, indent=2, ensure_ascii=False))