# 103 Calibrator 固件参考代码

## 目录说明

本目录保留103 Calibrator嵌入式固件的关键源代码，仅作为**参考用途**。

### 主要参考文件

| 文件 | 说明 |
|------|------|
| `Source/driver.c` | **核心参考** - 电机驱动控制逻辑 |
| `Source/driver.h` | 驱动头文件 |

### 其他支持文件

| 文件 | 说明 |
|------|------|
| `Source/tools.c` | 工具函数 |
| `Source/tools.h` | 工具头文件 |
| `Source/calibrator.c` | 校准逻辑 |
| `Source/calibrator.h` | 校准头文件 |
| `Source/main.c` | 主程序 |
| `Source/main.h` | 主程序头文件 |
| `Source/bootloader.c` | 引导程序 |
| `Source/bootloader.h` | 引导程序头文件 |
| `Source/cdc_acm_core.c` | USB CDC驱动 |
| `Source/cdc_acm_core.h` | USB CDC头文件 |
| `Source/def.h` | 定义文件 |
| `Source/usbd_conf.h` | USB配置 |
| `RTE/Device/GD32F103CB/` | GD32设备驱动 |

### 关键参考代码

#### 速度源选择 (driver.c)
```c
// instructionSelectSpeed() - 选择速度源
// reg=0 → P1-11 (SPD0=ON, SPD1=ON)
// reg=1 → P1-09 (SPD0=OFF, SPD1=ON)
// reg=2 → P1-10 (SPD0=ON, SPD1=OFF)
// reg=3 → 模拟输入 (SPD0=OFF, SPD1=OFF)
```

#### 伺服使能 (driver.c)
```c
// instructionSwitchServo() - 伺服使能/关闭
// DriverOn → 0x0001
// DriverOff → 0x0101
```

#### 速度设置 (driver.c)
```c
// instructionSetSpeed() - 设置速度
// P1-09/P1-10/P1-11 寄存器地址
```

#### 方向控制 (driver.c)
```c
// instructionSetDirection() - 设置方向
// CMDINV 信号控制方向
// 顺时针/逆时针
```

## 重要提示

- **Python驱动已实现**：所有功能已移植到Python驱动
- **仅作参考**：如需了解底层实现逻辑，可查阅driver.c
- **不再编译**：已删除编译产物（Objects/、Listings/等）

## 相关文档

- [ASDB2控制指南](../docs/drivers/device/ASDB2/ASDB2_CONTROL_GUIDE.md)
- [ASDB2电机驱动Python实现](../../backend/projects/encoder_test/drivers/device/ASDB2/asdb2_driver.py)