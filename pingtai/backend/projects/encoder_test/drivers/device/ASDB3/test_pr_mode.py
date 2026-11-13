"""ASDB3 PR模式测试脚本 - 0~360度循环控制

根据ASDB3手册，PR模式工作流程：
1. 连接时自动开通通讯控制权（P3-006=0x1FFF）
2. 切换到PR模式（P1-001=3）
3. 读取电子齿轮比（P1.044/P1.045）计算PUU/度
4. 设置共享PR参数（加减速时间、速度、延迟）
5. 设置PR路径（AUTO定位+JUMP跳转实现循环）
6. 使能伺服（P4-007 bit0=1）
7. 触发PR命令（P5-007=PR编号）
8. 监控执行状态（P5-007读取值）
9. 停止命令（P5-007=1000）

PR路径规划（0~360度，10度步长）：
- PR#01-PR#36: AUTO绝对定位（0°, 10°, 20°, ..., 350°）
- PR#37: JUMP跳转到PR#01（实现循环）
"""

import time
import logging
from projects.encoder_test.drivers.device.ASDB3.asdb3_driver import ASDB3Driver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ASDB3PRModeTest:
    """ASDB3 PR模式0~360度循环测试类"""

    def __init__(self, driver: ASDB3Driver):
        self.driver = driver
        self.puu_per_rev = 100000
        self.puu_per_degree = 0
        self.max_speed_rpm = 10.0
        self.test_running = False

    def _calc_puu_per_degree(self) -> bool:
        """根据电子齿轮比计算每度PUU数

        Returns:
            是否成功
        """
        gear = self.driver.read_e_gear_ratio()
        self.puu_per_rev = gear['puu_per_rev']
        self.puu_per_degree = self.puu_per_rev / 360.0
        logger.info(f"电子齿轮比: N={gear['numerator']}, M={gear['denominator']}")
        logger.info(f"每转PUU: {self.puu_per_rev}, 每度PUU: {self.puu_per_degree:.2f}")
        return True

    def setup_pr_mode(self) -> bool:
        """设置PR模式

        Returns:
            是否成功
        """
        logger.info("=== 开始设置PR模式 ===")

        try:
            # 1. 切换到PR模式
            logger.info("步骤1: 切换到PR模式")
            if not self.driver.set_control_mode(self.driver.CONTROL_MODE_PR):
                logger.error("切换到PR模式失败")
                return False
            time.sleep(0.2)

            # 2. 读取电子齿轮比
            logger.info("步骤2: 读取电子齿轮比")
            if not self._calc_puu_per_degree():
                logger.error("读取电子齿轮比失败")
                return False

            # 3. 设置共享PR参数
            logger.info("步骤3: 设置共享PR参数")

            acc_time_ms = 500
            dec_time_ms = 500

            if not self.driver.set_pr_shared_params('ACC', 0, acc_time_ms):
                logger.error("设置加速时间失败")
                return False

            if not self.driver.set_pr_shared_params('DEC', 0, dec_time_ms):
                logger.error("设置减速时间失败")
                return False

            if not self.driver.set_pr_shared_params('SPD', 0, self.max_speed_rpm):
                logger.error("设置速度失败")
                return False

            if not self.driver.set_pr_shared_params('DLY', 0, 0):
                logger.error("设置延迟时间失败")
                return False

            logger.info(f"共享参数: ACC={acc_time_ms}ms, DEC={dec_time_ms}ms, SPD={self.max_speed_rpm}RPM, DLY=0ms")

            # 4. 设置PR路径
            # 一次循环 = 0°递增到360° + 360°递减到0°
            # PR#01-PR#37: 0°, 10°, 20°, ..., 360°（递增）
            # PR#38-PR#73: 350°, 340°, ..., 0°（递减）
            # PR#74: JUMP跳转到PR#01（循环）
            logger.info("步骤4: 设置PR路径（0°→360°递增 + 360°→0°递减）")

            positions_up = list(range(0, 361, 10))    # [0, 10, ..., 360] 37个
            positions_down = list(range(350, -1, -10))  # [350, 340, ..., 0] 36个
            all_positions = positions_up + positions_down

            for i, angle in enumerate(all_positions):
                pr_number = i + 1
                position_puu = int(angle * self.puu_per_degree)

                direction = "递增" if i < len(positions_up) else "递减"
                logger.info(f"  PR#{pr_number:02d}: AUTO绝对定位 {angle}度 ({direction}) ({position_puu} PUU)")
                if not self.driver.set_pr_position_command(
                    pr_number=pr_number,
                    position_puu=position_puu,
                    pos_type='ABS',
                    acc_index=0,
                    dec_index=0,
                    dly_index=0,
                    spd_index=0,
                    interrupt=False,
                    overlap=False,
                    auto_next=True
                ):
                    logger.error(f"设置PR#{pr_number:02d}失败")
                    return False

                time.sleep(0.05)

            # 最后一个PR: JUMP跳转到PR#01（循环）
            jump_pr = len(all_positions) + 1
            logger.info(f"  PR#{jump_pr:02d}: JUMP跳转到PR#01（循环）")
            if not self.driver.set_pr_jump_command(
                pr_number=jump_pr,
                target_pr=1,
                dly_index=0,
                interrupt=False
            ):
                logger.error(f"设置PR#{jump_pr:02d}跳转命令失败")
                return False

            logger.info(f"PR路径设置完成: 递增{len(positions_up)}个 + 递减{len(positions_down)}个 + 1个跳转")

            # 5. 使能伺服
            logger.info("步骤5: 使能伺服")
            if not self.driver.enable_servo(True):
                logger.error("使能伺服失败")
                return False
            time.sleep(0.5)

            logger.info("=== PR模式设置完成 ===")
            return True

        except Exception as e:
            logger.error(f"设置PR模式失败: {e}")
            return False

    def run_pr_test(self, cycles: int = 1) -> bool:
        """运行PR测试

        通过P5-007监控PR执行状态：
        - 1-99: 正在执行
        - 10001-10099: 命令完成但电机未到位
        - 20001-20099: 命令完成且电机到位

        一次循环 = 0°递增到360° + 360°递减到0°
        循环判定：JUMP跳转到PR#01后，因0°位置相同，
        PR#01瞬间完成，P5-007直接跳到PR#02。所以检测PR#02
        再次出现且之前见过更大的PR号，即为一次循环完成。

        Args:
            cycles: 循环次数（0=无限循环）

        Returns:
            是否成功
        """
        logger.info(f"=== 开始PR测试（循环次数: {cycles if cycles > 0 else '无限'}） ===")

        try:
            self.test_running = True
            current_cycle = 0
            last_pr_number = 0
            max_pr_seen = 0
            positions_up = list(range(0, 361, 10))
            positions_down = list(range(350, -1, -10))
            all_positions = positions_up + positions_down

            logger.info("触发PR#01，开始运动")
            if not self.driver.trigger_pr_command(1):
                logger.error("触发PR#01失败")
                return False

            start_time = time.time()
            timeout = 600.0

            while self.test_running and (time.time() - start_time) < timeout:
                if cycles > 0 and current_cycle >= cycles:
                    logger.info(f"已完成{cycles}次循环，停止测试")
                    break

                pr_status = self.driver.get_pr_status()
                pr_num = pr_status.get('pr_number', 0)
                executing = pr_status.get('executing', False)
                completed = pr_status.get('completed', False)
                positioned = pr_status.get('positioned', False)

                if pr_num != last_pr_number and pr_num > 0:
                    last_pr_number = pr_num

                    if pr_num > max_pr_seen:
                        max_pr_seen = pr_num

                    # PR#02再次出现且之前见过更大的PR号 = 新循环开始
                    if pr_num == 2 and max_pr_seen > 2:
                        current_cycle += 1
                        max_pr_seen = pr_num
                        monitor = self.driver.get_pr_monitor_vars()
                        logger.info(f"=== 完成第{current_cycle}次循环 ===")
                        logger.info(f"  监控: Fb_PUU={monitor.get('fb_puu', 0)}, "
                                    f"Cmd_O={monitor.get('cmd_o', 0)}, "
                                    f"Err_PUU={monitor.get('err_puu', 0)}")

                    if pr_num <= len(all_positions):
                        angle = all_positions[pr_num - 1]
                        direction = "递增" if pr_num <= len(positions_up) else "递减"
                        if positioned:
                            logger.info(f"  PR#{pr_num:02d} 定位完成: {angle}度 ({direction})")
                        elif completed:
                            logger.info(f"  PR#{pr_num:02d} 命令完成: {angle}度 ({direction})，等待到位")
                        elif executing:
                            logger.info(f"  PR#{pr_num:02d} 执行中: {angle}度 ({direction})")
                    else:
                        logger.info(f"  PR#{pr_num:02d}: JUMP -> PR#01")

                time.sleep(0.1)

            if (time.time() - start_time) >= timeout:
                logger.warning(f"测试超时（{timeout}秒）")

            logger.info("=== PR测试完成 ===")
            return True

        except KeyboardInterrupt:
            logger.info("用户中断测试")
            self.test_running = False
            return True
        except Exception as e:
            logger.error(f"PR测试失败: {e}")
            self.test_running = False
            return False

    def stop_test(self):
        """停止测试"""
        logger.info("停止测试...")
        self.test_running = False

        try:
            self.driver.stop_pr_command()
            logger.info("PR命令已停止")
        except Exception as e:
            logger.warning(f"停止PR命令失败: {e}")

        try:
            self.driver.enable_servo(False)
            logger.info("伺服已关闭")
        except Exception as e:
            logger.warning(f"关闭伺服失败: {e}")

    def cleanup(self):
        """清理资源"""
        self.stop_test()


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python test_pr_mode.py <串口> [循环次数]")
        print("示例: python test_pr_mode.py COM8 3")
        print("示例: python test_pr_mode.py COM8 0  # 无限循环")
        sys.exit(1)

    port = sys.argv[1]
    cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    logger.info(f"=== ASDB3 PR模式测试 - 0~360度循环控制 ===")
    logger.info(f"串口: {port}")
    logger.info(f"循环次数: {cycles if cycles > 0 else '无限'}")
    logger.info(f"速度限制: 10 RPM")
    logger.info(f"位置范围: 0°→360°递增 + 360°→0°递减，步长10度")

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

        driver = ASDB3Driver(
            driver_id='asdb3_pr_test',
            protocol=modbus,
            slave_id=0x7F
        )

        logger.info("连接驱动器...")
        if not driver.connect():
            logger.error("连接驱动器失败")
            sys.exit(1)

        logger.info("驱动器连接成功")

        test = ASDB3PRModeTest(driver)

        try:
            if not test.setup_pr_mode():
                logger.error("设置PR模式失败")
                sys.exit(1)

            if not test.run_pr_test(cycles):
                logger.error("运行测试失败")
                sys.exit(1)

        finally:
            test.cleanup()
            driver.disconnect()

        logger.info("测试完成")

    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()