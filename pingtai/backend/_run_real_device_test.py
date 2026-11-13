import sys
import os
sys.path.insert(0, r'D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend')

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

from projects.encoder_test.drivers.device.encoder.dpt_encoder_analyzer import DPTEncoderAnalyzer
from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier
from projects.encoder_test.drivers.device.waveform_generator.dg811 import DG811WaveformGenerator
from projects.encoder_test.actions.power_amplifier_action import PowerAmplifierAction
from projects.encoder_test.actions.waveform_generator_action import WaveformGeneratorAction
from projects.encoder_test.actions.encoder_action import EncoderAction
from projects.encoder_test.core.testcase.encoder.encoder_power_cycle_case import EncoderPowerCycleCase
from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.protocol.custom_ascii_protocol import CustomASCIIProtocol
from shared.drivers.protocol.scpi_protocol import SCPIProtocol
import pyvisa

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("步骤1: 连接真实设备并测试编码器读数")
    logger.info("=" * 60)
    
    # 1. 连接编码器（Analyzer模式）
    logger.info("\n[1/3] 连接编码器...")
    encoder = DPTEncoderAnalyzer(port='COM6', baud_rate=2500000)
    if not encoder.connect():
        logger.error("❌ 编码器连接失败")
        return 1
    logger.info("✅ 编码器连接成功")
    
    # 测试编码器读数
    logger.info("\n测试编码器读数...")
    for i in range(5):
        result = encoder.read_both_angles()
        if result and result['crc_valid']:
            logger.info(f"  [{i+1}] 内圈: {result['inner']['angle_deg']:.4f}° | 外圈: {result['outer']['angle_deg']:.4f}° | CRC: ✅")
        else:
            logger.warning(f"  [{i+1}] 读取失败或CRC错误")
    
    # 2. 连接功率放大器
    logger.info("\n[2/3] 连接功率放大器...")
    try:
        comm = RS485Comm(driver_id='serial_pa', port='COM7', baudrate=9600)
        protocol = CustomASCIIProtocol(
            driver_id='ascii_pa',
            comm=comm,
            command_prefix='ATA,SET,',
            command_suffix=';',
            newline='\r\n'
        )
        power_amp = ATA101BPowerAmplifier(driver_id='power_amplifier', protocol=protocol)
        if not power_amp.connect():
            logger.error("❌ 功率放大器连接失败")
            encoder.disconnect()
            return 1
        logger.info("✅ 功率放大器连接成功")
    except Exception as e:
        logger.error(f"❌ 功率放大器连接异常: {e}")
        encoder.disconnect()
        return 1
    
    # 3. 连接波形发生器（直接使用pyvisa）
    logger.info("\n[3/3] 连接波形发生器...")
    try:
        rm = pyvisa.ResourceManager()
        resource_string = 'USB0::0x1AB1::0x0643::DG8A272500674::INSTR'
        instrument = rm.open_resource(resource_string)
        instrument.timeout = 5000
        instrument.write_termination = '\n'
        instrument.read_termination = '\n'
        
        # 测试通信
        idn = instrument.query('*IDN?')
        logger.info(f"波形发生器识别: {idn.strip()}")
        
        # 创建设备驱动（手动设置连接状态）
        from shared.drivers.comm.usb_visa_comm import USBVisaComm
        comm = USBVisaComm(driver_id='usb_tmc', vid=0x1AB1, pid=0x0643)
        comm._is_open = True
        comm._instrument = instrument
        comm._resource_manager = rm
        
        protocol = SCPIProtocol(driver_id='scpi', comm=comm)
        waveform_gen = DG811WaveformGenerator(driver_id='dg811', protocol=protocol)
        
        # 调用connect方法设置连接状态
        waveform_gen.connect()
        
        logger.info("✅ 波形发生器连接成功")
    except Exception as e:
        logger.error(f"❌ 波形发生器连接异常: {e}")
        power_amp.disconnect()
        encoder.disconnect()
        return 1
    
    logger.info("\n" + "=" * 60)
    logger.info("步骤2: 运行真实设备上断电测试")
    logger.info("=" * 60)
    
    # 运行真实设备测试
    runner = EncoderPowerCycleTestRunner()
    success = runner.run_real_device_test(power_amp, waveform_gen, encoder)
    runner.print_summary()
    
    # 断开设备
    logger.info("\n断开所有设备...")
    try:
        waveform_gen.disconnect()
    except:
        pass
    power_amp.disconnect()
    encoder.disconnect()
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✅ 真实设备测试完成")
    else:
        logger.error("❌ 真实设备测试失败")
    logger.info("=" * 60)
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())