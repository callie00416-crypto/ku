# 测试文件目录

## 📋 目录说明

本目录包含ATA-101B功率放大器的所有测试脚本，用于验证设备功能和调试通信问题。

## 🧪 测试文件列表

### 主要测试

- **test_comprehensive.py** - 全面测试
  - 测试所有设备功能
  - 验证参数设置
  - 检查设备状态
  - 适合首次测试

### 专项测试

- **test_newline_simple.py** - 回车换行符测试
  - 测试不同的回车换行符格式
  - 验证CRLF配置
  - ⚠️ 最重要的测试之一
  - 适合调试通信问题

- **test_protocol_direct.py** - 协议测试
  - 直接测试协议层
  - 验证命令构建
  - 测试响应解析
  - 适合协议验证

- **test_output_switch.py** - 输出开关测试
  - 专门测试输出开关功能
  - 循环测试开/关操作
  - 观察屏幕显示变化
  - 适合验证开关控制

- **test_screen_display.py** - 屏幕显示测试
  - 测试各种参数设置
  - 观察屏幕显示变化
  - 验证参数显示
  - 适合观察设备响应

## 🚀 使用指南

### 首次测试

如果是第一次测试设备，建议按照以下顺序：

1. **全面测试** - 验证基本功能
   ```bash
   cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
   python test_comprehensive.py
   ```

2. **回车换行符测试** - 验证通信配置
   ```bash
   cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
   python test_newline_simple.py
   ```

### 调试通信问题

如果遇到设备无响应的问题：

1. **回车换行符测试** - 最常见问题
   ```bash
   cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
   python test_newline_simple.py
   ```

2. **协议测试** - 验证协议层
   ```bash
   cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
   python test_protocol_direct.py
   ```

### 验证特定功能

如果需要验证特定功能：

1. **输出开关测试** - 验证开关控制
   ```bash
   cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
   python test_output_switch.py
   ```

2. **屏幕显示测试** - 观察设备响应
   ```bash
   cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
   python test_screen_display.py
   ```

## 📊 测试结果解读

### 成功标志

- ✅ `SET DONE!` - 命令执行成功
- ✅ 屏幕显示正确更新
- ✅ 参数设置生效
- ✅ 输出状态正确

### 失败标志

- ❌ `SET ERROR!` - 命令格式错误
- ❌ `OVER RANGE ERROR!` - 参数越界
- ❌ 无响应 - 通信问题
- ❌ 屏幕无变化 - 命令未生效

## ⚠️ 重要提示

### 回车换行符问题

这是ATA-101B设备最容易导致通信失败的问题：

1. **必须使用CRLF** (\r\n)
   - ✅ 正确：`ATA,SET,AON,0000;\r\n`
   - ❌ 错误：`ATA,SET,AON,0000;`
   - ❌ 错误：`ATA,SET,AON,0000;\n`
   - ❌ 错误：`ATA,SET,AON,0000;\r`

2. **技术说明**：
   - `\r` (CR, Carriage Return, 0x0D) - 回车符，光标回到行首
   - `\n` (LF, Line Feed, 0x0A) - 换行符，光标移动到下一行
   - `\r\n` (CRLF) - 回车换行符，先回车再换行

### 命令格式问题

1. **正确的命令前缀**：`ATA,SET,`
2. **错误的命令前缀**：`ATATATA,SET,`

### 响应格式问题

1. **正确的响应**：`SET DONE!` (有空格)
2. **错误的响应**：`SETDONE!` (无空格)

## 🔧 测试环境要求

### 硬件要求

- ✅ ATA-101B功率放大器设备
- ✅ USB数据线（设备自带）
- ✅ 电源线

### 软件要求

- ✅ Python 3.11+
- ✅ pyserial库
- ✅ 正确的工作目录

### 通信参数

- **端口**: COM3 (自动检测)
- **波特率**: 9600
- **数据位**: 8
- **停止位**: 1
- **校验位**: 无
- **回车换行符**: CRLF (\r\n)

## 📝 测试记录

建议记录每次测试的结果：

| 测试项 | 设置值 | 响应 | 屏幕显示 | 结果 | 备注 |
|--------|--------|------|----------|------|------|
| 全面测试 | - | - | - | ⬜ | |
| 回车换行符测试 | - | - | - | ⬜ | |
| 协议测试 | - | - | - | ⬜ | |
| 输出开关测试 | - | - | - | ⬜ | |
| 屏幕显示测试 | - | - | - | ⬜ | |

### 结果说明

- ✅ 通过：测试成功
- ❌ 失败：测试失败
- ⬜ 未测试：尚未进行测试

## 🎓 测试技巧

### 1. 逐步测试

建议按照以下顺序逐步测试：

1. 先测试回车换行符配置
2. 再测试协议层通信
3. 最后测试完整功能

### 2. 观察屏幕

每次测试时：

1. 观察屏幕显示变化
2. 记录显示内容
3. 验证参数是否正确

### 3. 查看日志

仔细查看测试日志：

1. 检查命令是否正确发送
2. 检查响应是否正确接收
3. 检查是否有错误信息

## 📞 技术支持

如果测试失败，请提供以下信息：

1. 测试文件名称
2. 错误信息和日志
3. 设备连接状态
4. 屏幕显示内容
5. 测试步骤和结果

---

**创建日期**: 2026-06-02  
**维护者**: Industrial Automation Platform  
**状态**: 活跃