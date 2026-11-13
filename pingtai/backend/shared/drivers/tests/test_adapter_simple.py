# -*- coding: utf-8 -*-
"""
简单测试 - 检查适配器是否正常工作
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        from projects.encoder_test.adapters.power_supply_adapter import PowerSupplyDeviceAdapter
        from platform_core.domain.common.enums import ProtocolType
        
        logger.info("开始测试适配器...")
        
        # 创建平台设备
        connection_params = PowerSupplyDeviceAdapter.create_connection_params(
            port='COM4',
            baudrate=9600,
            slave_id=1
        )
        
        device_params = PowerSupplyDeviceAdapter.create_device_params(
            channels=2,
            max_voltage=30.0,
            max_current=5.0
        )
        
        platform_device = PowerSupplyDeviceAdapter.to_platform_device(
            station_id=1,
            device_code="PS-001",
            device_name="可编程双路电源",
            protocol=ProtocolType.MODBUS_RTU,
            connection_params=connection_params,
            device_params=device_params
        )
        
        logger.info(f"平台设备创建成功: {platform_device}")
        logger.info(f"设备ID: {platform_device.id}")
        logger.info(f"设备代码: {platform_device.code}")
        logger.info(f"设备名称: {platform_device.name}")
        logger.info(f"设备类型: {platform_device.device_type.value}")
        
        # 测试反向转换
        device_dto = PowerSupplyDeviceAdapter.from_platform_device(platform_device)
        logger.info(f"设备DTO: {device_dto}")
        
        logger.info("[SUCCESS] 适配器测试通过！")
        return 0
        
    except Exception as e:
        logger.error(f"[FAIL] 适配器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())