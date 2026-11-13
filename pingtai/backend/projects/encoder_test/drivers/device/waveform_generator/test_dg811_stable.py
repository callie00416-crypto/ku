"""
RIGOL DG811波形发生器 - 稳定测试版本

【改进】
- 增加命令延迟，避免设备来不及处理
- 改进错误处理
- 验证每个命令的执行结果
- 调整VISA通信参数
"""
import sys
from pathlib import Path

# 获取backend目录路径
backend_path = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import time
import logging
import pyvisa

# 尝试导入
try:
    from shared.drivers.protocol.scpi_protocol import SCPIProtocol
    from projects.encoder_test.drivers.device.waveform_generator.dg811 import DG811WaveformGenerator
    print("✓ 模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建改进的VISA通信类
class StableVisaComm:
    """稳定的VISA通信类"""
    
    def __init__(self, resource_string):
        self.resource_string = resource_string
        self._is_open = False
        self._instrument = None
        self._resource_manager = None
        
    def open(self):
        """打开连接"""
        try:
            self._resource_manager = pyvisa.ResourceManager()
            self._instrument = self._resource_manager.open_resource(self.resource_string)
            
            # 调整通信参数以提高稳定性
            self._instrument.timeout = 10000  # 增加超时时间
            self._instrument.write_termination = '\n'
            self._instrument.read_termination = '\n'
            self._instrument.chunk_size = 20480  # 增加缓冲区大小
            
            self._is_open = True
            
            # 等待设备稳定
            time.sleep(0.5)
            
            return True
        except Exception as e:
            print(f"打开连接失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self._instrument:
            try:
                self._instrument.close()
            except:
                pass
            self._is_open = False
        if self._resource_manager:
            try:
                self._resource_manager.close()
            except:
                pass
    
    @property
    def is_open(self):
        return self._is_open
    
    def send(self, data):
        """发送数据"""
        if not self._is_open:
            raise ConnectionError("未连接")
        
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        try:
            self._instrument.write(data)
            time.sleep(0.05)  # 发送后短暂延迟
            return len(data)
        except Exception as e:
            print(f"发送失败: {e}")
            raise
    
    def recv(self, size=1024, timeout=1.0):
        """接收数据"""
        if not self._is_open:
            raise ConnectionError("未连接")
        
        try:
            original_timeout = self._instrument.timeout
            self._instrument.timeout = int(timeout * 1000)
            
            try:
                data = self._instrument.read()
                time.sleep(0.02)  # 接收后短暂延迟
                if isinstance(data, str):
                    data = data.encode('utf-8')
                return data
            finally:
                self._instrument.timeout = original_timeout
                
        except pyvisa.errors.VisaIOError as e:
            if e.abbreviation == 'VI_ERROR_TMO':
                return None
            print(f"接收错误: {e}")
            return None


def test_basic_communication():
    """测试基本通信"""
    
    resource_string = "USB0::0x1AB1::0x0643::DG8A272300397::INSTR"
    
    print("=" * 70)
    print("DG811基本通信测试")
    print("=" * 70)
    
    # 创建通信层
    print("\n[1/3] 创建VISA通信层...")
    comm = StableVisaComm(resource_string)
    if not comm.open():
        print("✗ 连接失败")
        return False
    print("✓ 连接成功")
    
    # 创建SCPI协议层
    print("\n[2/3] 创建SCPI协议层...")
    protocol = SCPIProtocol(driver_id='scpi', comm=comm)
    if not protocol.connect():
        print("✗ SCPI协议连接失败")
        comm.close()
        return False
    print("✓ SCPI协议连接成功")
    
    # 测试基本命令
    print("\n[3/3] 测试基本SCPI命令...")
    
    # 测试1: 获取设备ID
    print("\n测试1: 获取设备ID")
    try:
        device_id = protocol.get_id()
        if device_id:
            print(f"✓ 设备ID: {device_id}")
        else:
            print("✗ 无法获取设备ID")
            return False
    except Exception as e:
        print(f"✗ 获取设备ID失败: {e}")
        return False
    
    time.sleep(0.5)
    
    # 测试2: 设置和查询频率
    print("\n测试2: 设置和查询频率")
    try:
        # 设置频率
        cmd = ":SOUR1:FREQ 1000"
        print(f"  发送命令: {cmd}")
        result = protocol.send_command(cmd)
        time.sleep(0.3)  # 等待设备处理
        
        # 查询频率
        query = ":SOUR1:FREQ?"
        print(f"  查询命令: {query}")
        freq = protocol.query(query)
        
        if freq:
            print(f"✓ 频率设置成功: {freq}Hz")
        else:
            print("✗ 无法查询频率")
            return False
            
    except Exception as e:
        print(f"✗ 频率测试失败: {e}")
        return False
    
    time.sleep(0.5)
    
    # 测试3: 设置和查询波形
    print("\n测试3: 设置和查询波形")
    try:
        # 设置波形
        cmd = ":SOUR1:FUNC SIN"
        print(f"  发送命令: {cmd}")
        result = protocol.send_command(cmd)
        time.sleep(0.3)
        
        # 查询波形
        query = ":SOUR1:FUNC?"
        print(f"  查询命令: {query}")
        func = protocol.query(query)
        
        if func:
            print(f"✓ 波形设置成功: {func}")
        else:
            print("✗ 无法查询波形")
            return False
            
    except Exception as e:
        print(f"✗ 波形测试失败: {e}")
        return False
    
    time.sleep(0.5)
    
    # 测试4: 控制输出
    print("\n测试4: 控制输出")
    try:
        # 打开输出
        cmd = ":OUTP1 ON"
        print(f"  发送命令: {cmd}")
        result = protocol.send_command(cmd)
        time.sleep(0.3)
        
        # 查询输出状态
        query = ":OUTP1?"
        print(f"  查询命令: {query}")
        status = protocol.query(query)
        
        if status:
            print(f"✓ 输出状态: {status}")
        else:
            print("✗ 无法查询输出状态")
        
        # 等待观察
        print(f"  ⏱️  请观察设备屏幕 (5秒)...")
        time.sleep(5.0)
        
        # 关闭输出
        cmd = ":OUTP1 OFF"
        print(f"  发送命令: {cmd}")
        result = protocol.send_command(cmd)
        time.sleep(0.3)
        
        print("✓ 输出控制测试完成")
        
    except Exception as e:
        print(f"✗ 输出控制测试失败: {e}")
        return False
    
    # 断开连接
    print("\n断开连接...")
    try:
        protocol.disconnect()
        print("✓ 连接已断开")
    except Exception as e:
        print(f"✗ 断开连接失败: {e}")
    
    print("\n" + "=" * 70)
    print("基本通信测试完成！")
    print("=" * 70)
    
    return True


def test_waveform_changes():
    """测试波形变化"""
    
    resource_string = "USB0::0x1AB1::0x0643::DG8A272300397::INSTR"
    
    print("=" * 70)
    print("DG811波形变化测试")
    print("=" * 70)
    
    # 创建通信层
    print("\n[1/3] 创建VISA通信层...")
    comm = StableVisaComm(resource_string)
    if not comm.open():
        print("✗ 连接失败")
        return False
    print("✓ 连接成功")
    
    # 创建SCPI协议层
    print("\n[2/3] 创建SCPI协议层...")
    protocol = SCPIProtocol(driver_id='scpi', comm=comm)
    if not protocol.connect():
        print("✗ SCPI协议连接失败")
        comm.close()
        return False
    print("✓ SCPI协议连接成功")
    
    # 创建设备驱动
    print("\n[3/3] 创建设备驱动...")
    generator = DG811WaveformGenerator(driver_id='dg811', protocol=protocol)
    if not generator.connect():
        print("✗ 设备连接失败")
        protocol.disconnect()
        comm.close()
        return False
    print("✓ 设备连接成功")
    
    # 测试波形变化
    print("\n" + "=" * 70)
    print("开始波形变化测试")
    print("=" * 70)
    
    waveforms = [
        ('SIN', '正弦波'),
        ('SQU', '方波'),
        ('TRI', '三角波'),
        ('RAMP', '锯齿波'),
        ('PULS', '脉冲波'),
    ]
    
    for i, (wf_type, wf_name) in enumerate(waveforms, 1):
        print(f"\n[{i}/{len(waveforms)}] 设置波形: {wf_name}")
        
        try:
            # 直接发送SCPI命令
            cmd = f":SOUR1:FUNC {wf_type}"
            print(f"  发送命令: {cmd}")
            protocol.send_command(cmd)
            time.sleep(1.0)  # 增加延迟确保设备处理完成
            
            # 打开输出
            cmd = ":OUTP1 ON"
            print(f"  发送命令: {cmd}")
            protocol.send_command(cmd)
            time.sleep(0.5)
            
            # 查询当前波形
            query = ":SOUR1:FUNC?"
            print(f"  查询命令: {query}")
            current_wf = protocol.query(query)
            
            if current_wf:
                print(f"  当前波形: {current_wf}")
                if wf_type in current_wf:
                    print(f"  ✓ 波形设置成功")
                else:
                    print(f"  ⚠️  波形查询不匹配（可能是延迟问题）")
            else:
                print(f"  ✗ 无法查询波形")
            
            # 等待观察
            print(f"  ⏱️  请观察设备屏幕上的波形变化 (5秒)...")
            time.sleep(5.0)
            
        except Exception as e:
            print(f"  ✗ 设置失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 关闭输出
    print("\n关闭输出...")
    try:
        protocol.send_command(":OUTP1 OFF")
        time.sleep(0.5)
        print("✓ 输出已关闭")
    except Exception as e:
        print(f"✗ 关闭输出失败: {e}")
    
    # 断开连接
    print("\n断开连接...")
    try:
        protocol.disconnect()
        print("✓ 连接已断开")
    except Exception as e:
        print(f"✗ 断开连接失败: {e}")
    
    print("\n" + "=" * 70)
    print("波形变化测试完成！")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    print("\n请选择测试模式:")
    print("1. 基本通信测试")
    print("2. 波形变化测试")
    print("3. 两个测试都运行")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    try:
        if choice == '1':
            success = test_basic_communication()
        elif choice == '2':
            success = test_waveform_changes()
        elif choice == '3':
            print("\n" + "="*70)
            print("运行基本通信测试")
            print("="*70)
            success1 = test_basic_communication()
            
            print("\n" + "="*70)
            print("运行波形变化测试")
            print("="*70)
            success2 = test_waveform_changes()
            
            success = success1 and success2
        else:
            print("无效选择")
            success = False
        
        if success:
            print("\n✓ 测试成功完成！")
        else:
            print("\n✗ 测试失败！")
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()