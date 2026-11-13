"""
ATA-101B 功放协议验证脚本

【功能】
严格按照协议文档发送命令，验证通信是否正常
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import serial


# ===== 配置区 =====
SERIAL_PORT = 'COM3'
BAUDRATE = 9600
# ==================


def test_protocol():
    """测试协议通信"""
    print("="*70)
    print("ATA-101B 功放协议验证")
    print("="*70)
    
    print(f"\n串口配置:")
    print(f"  端口: {SERIAL_PORT}")
    print(f"  波特率: {BAUDRATE}")
    print(f"  数据位: 8")
    print(f"  校验位: None")
    print(f"  停止位: 1")
    print(f"  流控制: None\n")
    
    try:
        # 打开串口
        print("="*70)
        print("步骤1: 打开串口")
        print("="*70)
        
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=2
        )
        
        print(f"✅ 串口 {SERIAL_PORT} 打开成功\n")
        
        # 测试协议命令
        print("="*70)
        print("步骤2: 发送协议命令")
        print("="*70)
        
        # 根据协议文档的完整命令列表
        protocol_commands = [
            ("1. 输出开", "ATA,SET,AON,0000;"),
            ("2. 输出关", "ATA,SET,AOF,0000;"),
            ("3. 保存设置", "ATA,SET,SAV,0000;"),
            ("4. 输入电阻 50Ω", "ATA,SET,RIN,0050;"),
            ("5. 输入电阻 1000Ω", "ATA,SET,RIN,1000;"),
            ("6. 输出电阻 1.5Ω", "ATA,SET,ROT,0015;"),
            ("7. 输出电阻 50Ω", "ATA,SET,ROT,0500;"),
            ("8. 增益 0dB", "ATA,SET,AMP,0000;"),
            ("9. 增益 12dB", "ATA,SET,AMP,0012;"),
            ("10. 增益 20dB", "ATA,SET,AMP,0020;"),
        ]
        
        results = []
        
        for name, command in protocol_commands:
            print(f"\n{'='*70}")
            print(f"测试: {name}")
            print(f"{'='*70}")
            
            # 清空缓冲区
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # 显示发送的数据
            print(f"\n发送命令: {command}")
            command_bytes = command.encode('ascii')
            print(f"字节数: {len(command_bytes)}")
            print(f"十六进制: {' '.join(f'{b:02X}' for b in command_bytes)}")
            
            # 发送命令
            bytes_sent = ser.write(command_bytes)
            ser.flush()
            print(f"已发送: {bytes_sent} 字节")
            
            # 等待设备响应（给设备足够时间处理）
            print("等待响应...")
            time.sleep(1.0)
            
            # 读取所有可用数据
            response_bytes = ser.read_all()
            
            if response_bytes:
                response_str = response_bytes.decode('ascii', errors='replace').strip()
                print(f"\n✅ 收到响应:")
                print(f"  ASCII: {response_str}")
                print(f"  字节: {len(response_bytes)}")
                print(f"  十六进制: {' '.join(f'{b:02X}' for b in response_bytes)}")
                
                # 判断响应类型
                if "SET DONE!" in response_str:
                    print(f"  结果: ✅ 设置成功")
                    results.append((name, "SUCCESS", response_str))
                elif "OVER RANGE ERROR!" in response_str:
                    print(f"  结果: ❌ 参数越界")
                    results.append((name, "OVER_RANGE", response_str))
                elif "SET ERROR!" in response_str:
                    print(f"  结果: ❌ 命令错误")
                    results.append((name, "ERROR", response_str))
                else:
                    print(f"  结果: ️  未知响应")
                    results.append((name, "UNKNOWN", response_str))
            else:
                print(f"\n❌ 未收到响应（超时）")
                results.append((name, "NO_RESPONSE", ""))
                
                print(f"\n  可能原因:")
                print(f"    1. 功放设备未通电")
                print(f"    2. RS485 A/B 线接反")
                print(f"    3. 设备忙，正在处理其他命令")
                print(f"    4. 需要设备初始化")
            
            # 命令间隔
            time.sleep(0.5)
        
        # 测试结果汇总
        print(f"\n\n{'='*70}")
        print("测试结果汇总")
        print(f"{'='*70}\n")
        
        success_count = sum(1 for _, status, _ in results if status == "SUCCESS")
        fail_count = sum(1 for _, status, _ in results if status != "SUCCESS")
        
        print(f"总测试数: {len(results)}")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}\n")
        
        print(f"{'序号':<5} {'测试项':<20} {'状态':<15} {'响应'}")
        print("-" * 70)
        
        for i, (name, status, response) in enumerate(results, 1):
            status_icon = {
                "SUCCESS": "✅",
                "OVER_RANGE": "❌",
                "ERROR": "❌",
                "UNKNOWN": "️ ",
                "NO_RESPONSE": "❌"
            }.get(status, "?")
            
            print(f"{i:<5} {name:<20} {status_icon} {status:<10} {response[:30]}")
        
        print(f"\n{'='*70}")
        
        # 关闭串口
        ser.close()
        print(f"\n✅ 串口已关闭\n")
        
        # 给出建议
        if success_count == 0:
            print("="*70)
            print("诊断建议")
            print("="*70)
            print("""
所有命令都未收到响应，请检查：

1. 硬件连接
   - 确认功放设备已通电（查看电源指示灯）
   - 检查 RS485 接线是否正确：
     * 功放 A+  → USB转RS485 A+
     * 功放 B-  → USB转RS485 B-
     * 功放 GND → USB转RS485 GND（可选）
   
2. 尝试交换 A/B 线
   - RS485 的 A 和 B 可能接反了
   - 交换后重新测试

3. 使用串口调试助手
   - 下载串口调试工具（如 SSCOM）
   - 手动发送命令: ATA,SET,AON,0000;
   - 查看是否能收到响应

4. 检查设备手册
   - 确认是否需要特殊初始化
   - 确认设备是否处于远程控制模式
   - 查看是否有其他通信要求

5. 联系设备厂商
   - 确认设备固件版本
   - 确认协议版本是否匹配
""")
        else:
            print(f"\n✅ 有 {success_count} 个命令测试成功，通信正常！\n")
        
    except serial.SerialException as e:
        print(f"\n 串口错误: {e}\n")
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断\n")
    except Exception as e:
        print(f"\n❌ 异常: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_protocol()
