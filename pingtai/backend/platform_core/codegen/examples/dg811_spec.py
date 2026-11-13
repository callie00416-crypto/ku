"""
DG811波形发生器设备规范 - 基于通用模板

【设备信息】
- 厂商: RIGOL
- 型号: DG811
- 序列号: DG8A272300397
- 协议: SCPI
- 通信: USB VISA
- 通道: 双通道
"""

DG811_SPEC = {
    "device_name": "waveform_generator",
    "class_name": "DG811WaveformGenerator",
    "description": "RIGOL DG811双通道函数/任意波形发生器",
    
    "manufacturer": "RIGOL",
    "model": "DG811",
    "serial_number": "DG8A272300397",
    "firmware_version": "00.02.06.00.01",
    
    "protocol": {
        "type": "scpi",
        "version": "1999.0",
        "description": "标准命令可编程仪器协议"
    },
    
    "communication": {
        "type": "usb_visa",
        "description": "USB VISA通信",
        "config": {
            "resource_string": "USB0::0x1AB1::0x0643::DG8A272300397::INSTR",
            "vid": 0x1AB1,
            "pid": 0x0643,
            "timeout": 10000
        }
    },
    
    "channels": 2,
    "channel_prefix": "CH",
    
    "scpi_config": {
        "device_commands": {
            "get_id": "*IDN?",
            "reset": "*RST",
            "clear": "*CLS",
            "get_error": "SYST:ERR?",
            "get_options": "*OPT?"
        },
        
        "channel_commands": {
            "waveform": {
                "set": ":SOUR{channel}:FUNC {waveform}",
                "get": ":SOUR{channel}:FUNC?",
                "description": "波形类型"
            },
            "frequency": {
                "set": ":SOUR{channel}:FREQ {frequency}",
                "get": ":SOUR{channel}:FREQ?",
                "description": "频率",
                "unit": "Hz"
            },
            "amplitude": {
                "set": ":SOUR{channel}:VOLT {amplitude}",
                "get": ":SOUR{channel}:VOLT?",
                "description": "幅度",
                "unit": "Vpp"
            },
            "offset": {
                "set": ":SOUR{channel}:VOLT:OFFS {offset}",
                "get": ":SOUR{channel}:VOLT:OFFS?",
                "description": "偏置",
                "unit": "V"
            },
            "phase": {
                "set": ":SOUR{channel}:PHAS {phase}",
                "get": ":SOUR{channel}:PHAS?",
                "description": "相位",
                "unit": "deg"
            },
            "output": {
                "on": ":OUTP{channel} ON",
                "off": ":OUTP{channel} OFF",
                "get": ":OUTP{channel}?",
                "description": "输出控制"
            }
        },
        
        "response_parser": {
            "default": "strip",
            "frequency": "float",
            "amplitude": "float",
            "offset": "float",
            "phase": "float"
        },
        
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
    
    "init_commands": [
        "*RST",
        "*CLS",
        ":OUTP1 OFF",
        ":OUTP2 OFF"
    ],
    
    "methods": [
        {
            "name": "connect",
            "description": "连接设备",
            "parameters": [],
            "return_type": "bool"
        },
        {
            "name": "disconnect",
            "description": "断开设备",
            "parameters": [],
            "return_type": "None"
        },
        {
            "name": "set_waveform",
            "description": "设置波形参数",
            "parameters": [
                {"name": "waveform", "type": "str"},
                {"name": "frequency", "type": "float"},
                {"name": "amplitude", "type": "float"},
                {"name": "offset", "type": "float"},
                {"name": "phase", "type": "float"},
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        },
        {
            "name": "set_frequency",
            "description": "设置频率",
            "parameters": [
                {"name": "frequency", "type": "float"},
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        },
        {
            "name": "set_amplitude",
            "description": "设置幅度",
            "parameters": [
                {"name": "amplitude", "type": "float"},
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        },
        {
            "name": "set_offset",
            "description": "设置偏置",
            "parameters": [
                {"name": "offset", "type": "float"},
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        },
        {
            "name": "set_phase",
            "description": "设置相位",
            "parameters": [
                {"name": "phase", "type": "float"},
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        },
        {
            "name": "output_on",
            "description": "打开输出",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        },
        {
            "name": "output_off",
            "description": "关闭输出",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        },
        {
            "name": "get_waveform",
            "description": "获取波形类型",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "str"
        },
        {
            "name": "get_frequency",
            "description": "获取频率",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "float"
        },
        {
            "name": "get_amplitude",
            "description": "获取幅度",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "float"
        },
        {
            "name": "get_offset",
            "description": "获取偏置",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "float"
        },
        {
            "name": "get_phase",
            "description": "获取相位",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "float"
        },
        {
            "name": "get_output_status",
            "description": "获取输出状态",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        },
        {
            "name": "read_status",
            "description": "读取通道状态",
            "parameters": [
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "Dict[str, Any]"
        },
        {
            "name": "read_data",
            "description": "读取双通道数据",
            "parameters": [],
            "return_type": "Dict[str, Any]"
        },
        {
            "name": "reset",
            "description": "重置设备",
            "parameters": [],
            "return_type": "bool"
        },
        {
            "name": "health_check",
            "description": "健康检查",
            "parameters": [],
            "return_type": "Dict[str, Any]"
        },
        {
            "name": "get_device_info",
            "description": "获取设备信息",
            "parameters": [],
            "return_type": "Dict[str, Any]"
        }
    ],
    
    "events": {
        "on_connect": "device_connected",
        "on_disconnect": "device_disconnected",
        "on_error": "device_error",
        "on_operation_success": "operation_success",
        "on_operation_failure": "operation_failure"
    },
    
    "metadata": {
        "author": "Industrial Automation Platform",
        "version": "1.0.0",
        "created": "2026-06-01",
        "modified": "2026-06-01",
        "notes": "基于通用设备规范模板生成"
    }
}