"""ASDB3 PR模式简化测试脚本

根据ASDB3手册，PR模式工作流程：
1. 设置P3-006=0x1FFF开通通讯控制权（connect时自动完成）
2. 切换到PR模式（P1-001=3）
3. 设置共享PR参数（加减速时间、速度、延迟）
4. 设置PR路径（P6.002/P6.003等）
5. 使能伺服（P4-007 bit0=1）
6. 触发PR命令（P5-007=PR编号）
7. 监控执行状态（P5-007读取值）
8. 停止命令（P5-007=1000）
"""

import time
import logging
from projects.encoder_test.drivers.device.ASDB3.asdb3_driver import ASDB3Driver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def simple_pr_test(driver: ASDB3Driver):
    """简单的PR测试

    测试流程：
    1. 确认PR模式
    2. 设置PR#01为位置命令（绝对定位10000 PUU）
    3. 使能伺服
    4. 触发PR#01
    5. 监控执行状态
    6. 停止并关闭伺服
    """
    logger.info("=== 开始简单PR测试 ===")

    try:
        # 1. 确认PR模式
        logger.info("步骤1: 确认PR模式")
        data = driver.read_data()
        logger.info(f"  当前状态: {data}")

        # 2. 设置共享PR参数
        logger.info("步骤2: 设置共享PR参数")

        # 加速时间#0 = 200ms (P5.020)
        driver.set_pr_shared_params('ACC', 0, 200)
        # 减速时间#0 = 200ms (P5.020，ACC和DEC共用同一组)
        driver.set_pr_shared_params('DEC', 0, 200)
        # 目标速度#0 = 100.0 RPM (P5.060)
        driver.set_pr_shared_params('SPD', 0, 100.0)
        # 延迟时间#0 = 0ms (P5.040)
        driver.set_pr_shared_params('DLY', 0, 0)

        logger.info("  共享参数设置完成: ACC=200ms, DEC=200ms, SPD=100RPM, DLY=0ms")

        # 3. 设置PR#01: 绝对定位 10000 PUU
        # TYPE=0x02(SINGLE), ACC=0, DEC=0, SPD=0, DLY=0
        logger.info("步骤3: 设置PR#01 = 绝对定位 10000 PUU")
        driver.set_pr_position_command(
            pr_number=1,
            position_puu=10000,
            pos_type='ABS',
            acc_index=0,
            dec_index=0,
            dly_index=0,
            spd_index=0,
            interrupt=False,
            overlap=False,
            auto_next=False
        )

        # 验证写入
        addr_p6_002 = driver.calc_addr(6, 2)
        addr_p6_003 = driver.calc_addr(6, 3)
        prop_regs = driver.modbus.read_registers(address=addr_p6_002, count=2, slave_id=driver.slave_id)
        data_regs = driver.modbus.read_registers(address=addr_p6_003, count=2, slave_id=driver.slave_id)
        if prop_regs:
            prop_value = (prop_regs[1] << 16) | prop_regs[0]
            logger.info(f"  P6.002 = 0x{prop_value:08X}")
        if data_regs:
            data_value = (data_regs[1] << 16) | data_regs[0]
            logger.info(f"  P6.003 = {data_value}")

        # 4. 使能伺服
        logger.info("步骤4: 使能伺服")
        if not driver.enable_servo(True):
            logger.error("使能伺服失败")
            return False
        time.sleep(0.5)
        logger.info("  伺服已使能")

        # 5. 触发PR#01
        logger.info("步骤5: 触发PR#01 (P5-007=1)")
        if not driver.trigger_pr_command(1):
            logger.error("触发PR#01失败")
            return False
        logger.info("  PR#01已触发")

        # 6. 监控执行状态
        logger.info("步骤6: 监控执行状态")

        start_time = time.time()
        timeout = 30.0

        while (time.time() - start_time) < timeout:
            pr_status = driver.get_pr_status()
            pr_num = pr_status.get('pr_number', 0)
            executing = pr_status.get('executing', False)
            completed = pr_status.get('completed', False)
            positioned = pr_status.get('positioned', False)
            raw = pr_status.get('raw', 0)

            logger.info(f"  P5-007={raw}, PR#{pr_num}, executing={executing}, completed={completed}, positioned={positioned}")

            if positioned:
                logger.info("  定位完成！电机已到达目标位置")
                break

            if completed and not positioned:
                logger.info("  命令完成，等待电机到位...")

            time.sleep(0.3)

        # 读取监控变量
        monitor = driver.get_pr_monitor_vars()
        logger.info(f"  监控: Fb_PUU={monitor.get('fb_puu', 0)}, Cmd_O={monitor.get('cmd_o', 0)}, "
                    f"Err_PUU={monitor.get('err_puu', 0)}, Cmd_E={monitor.get('cmd_e', 0)}")

        # 7. 停止并关闭伺服
        logger.info("步骤7: 停止并关闭伺服")
        driver.stop_pr_command()
        time.sleep(0.5)
        driver.enable_servo(False)
        logger.info("  伺服已关闭")

        logger.info("=== 简单PR测试完成 ===")
        return True

    except Exception as e:
        logger.error(f"简单PR测试失败: {e}")
        import traceback
        traceback.print_exc()

        try:
            driver.stop_pr_command()
            driver.enable_servo(False)
        except Exception:
            pass

        return False


def main():
    """主函数"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python test_pr_simple.py <串口>")
        print("示例: python test_pr_simple.py COM3")
        sys.exit(1)

    port = sys.argv[1]

    logger.info(f"=== ASDB3 PR模式简化测试 ===")
    logger.info(f"串口: {port}")

    try:
        from shared.drivers.comm.rs485_comm import RS485Comm
        from shared.drivers.protocol.modbus_rtu import ModbusDriver

        comm = RS485Comm(
            driver_id='rs485_asdb3',
            port=port,
            baudrate=115200,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1.0
        )

        modbus = ModbusDriver(
            driver_id='modbus_asdb3',
            comm=comm,
            slave_id=0x7F,
            mode='rtu'
        )

        # 创建ASDB3驱动
        driver = ASDB3Driver(
            driver_id='asdb3_simple_test',
            protocol=modbus,
            slave_id=0x7F
        )

        # 连接驱动器
        logger.info("连接驱动器...")
        if not driver.connect():
            logger.error("连接驱动器失败")
            sys.exit(1)

        logger.info("✓ 驱动器连接成功")

        try:
            # 运行简单测试
            if not simple_pr_test(driver):
                logger.error("简单测试失败")
                sys.exit(1)

        finally:
            # 断开连接
            driver.disconnect()
            logger.info("✓ 驱动器已断开")

        logger.info("测试完成")

    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        logger.error("请确保已安装所需的依赖模块")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()