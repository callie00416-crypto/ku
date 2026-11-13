# 归档文件目录

## 📋 目录说明

本目录包含调试和开发过程中使用的辅助工具和脚本，这些文件在正常使用中不需要，但可能在故障排除或进一步开发时有用。

## 📦 文件列表

### 诊断工具

- **deep_diagnose.py** - 深度诊断工具
  - 用于深入分析设备通信问题
  - 提供详细的通信日志
  - 分析协议响应

- **diagnose_device.py** - 设备诊断工具
  - 基础设备连接诊断
  - 通信参数验证
  - 基本功能测试

### 检测工具

- **detect_usb_device.py** - USB设备检测工具
  - 自动检测USB设备
  - 识别设备类型
  - 确定串口号

### 文档工具

- **read_pdf_manual.py** - PDF手册阅读工具
  - 提取设备手册文本
  - 分析协议文档
  - 查找关键信息

### 通信助手

- **serial_assistant_for_manufacturer.py** - 串口助手工具
  - 提供串口通信辅助功能
  - 用于与厂商技术支持沟通
  - 生成诊断报告

## 🚀 使用场景

### 1. 设备连接问题

如果遇到设备连接问题，可以使用：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/archive
python detect_usb_device.py
```

### 2. 通信协议问题

如果遇到通信协议问题，可以使用：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/archive
python deep_diagnose.py
```

### 3. 需要联系厂商

如果需要联系厂商技术支持，可以使用：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/archive
python serial_assistant_for_manufacturer.py
```

### 4. 查看设备手册

如果需要查看设备手册内容，可以使用：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/archive
python read_pdf_manual.py
```

## ⚠️ 注意事项

1. **仅在需要时使用**：这些工具主要用于故障排除，正常使用不需要运行。

2. **需要设备连接**：大多数工具需要设备已连接才能正常工作。

3. **查看日志**：运行这些工具时，请仔细查看输出日志。

4. **保存诊断结果**：如果遇到问题，建议保存诊断结果以便分析。

## 📞 技术支持

如果使用这些工具后仍无法解决问题，请：

1. 保存所有诊断日志
2. 记录设备型号和序列号
3. 描述问题的详细情况
4. 联系技术支持团队

---

**归档日期**: 2026-06-02  
**维护者**: Industrial Automation Platform  
**状态**: 已归档