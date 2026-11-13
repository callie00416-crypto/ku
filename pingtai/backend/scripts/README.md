# 脚本目录

## 📋 目录说明

本目录包含各种临时测试脚本和诊断工具，用于开发过程中的调试和验证。

## 🛠️ 脚本列表

### Modbus相关脚本

- **check_modbus_client.py** - Modbus客户端检查脚本
  - 用于测试Modbus客户端连接
  - 验证Modbus通信功能
  - 调试Modbus相关问题

- **check_pymodbus_api.py** - PyModbus API检查脚本
  - 测试PyModbus库的API
  - 验证API兼容性
  - 检查函数签名

### 设备诊断脚本

- **diagnose_power_supply.py** - 电源设备诊断脚本
  - 诊断电源设备连接
  - 测试电源设备通信
  - 验证电源设备功能

### 测试运行脚本

- **run_real_60_hour_tests.py** - 运行真实60小时测试
  - 执行长时间稳定性测试
  - 验证系统长期运行能力
  - 生成测试报告

- **run_unit_tests.py** - 运行单元测试
  - 执行所有单元测试
  - 生成测试覆盖率报告
  - 验证代码质量

- **run_60_hour_tests.py** - 运行60小时测试
  - 执行标准60小时测试
  - 验证设备稳定性
  - 记录测试数据

- **run_13_hour_tests_fixed.py** - 运行13小时测试（修复版）
  - 执行修复后的13小时测试
  - 验证修复效果
  - 对比测试结果

### 验证和分析脚本

- **validate_test_fixes.py** - 验证测试修复
  - 验证测试修复效果
  - 检查修复完整性
  - 生成验证报告

- **reanalyze_protocol.py** - 重新分析协议
  - 重新分析设备协议
  - 验证协议实现
  - 生成协议文档

- **read_protocol_doc.py** - 读取协议文档
  - 读取设备协议文档
  - 提取协议信息
  - 生成协议摘要

## 🚀 使用方法

### Modbus客户端检查

```bash
cd backend/scripts
python check_modbus_client.py
```

### PyModbus API检查

```bash
cd backend/scripts
python check_pymodbus_api.py
```

### 电源设备诊断

```bash
cd backend/scripts
python diagnose_power_supply.py
```

### 运行真实60小时测试

```bash
cd backend/scripts
python run_real_60_hour_tests.py
```

### 运行单元测试

```bash
cd backend/scripts
python run_unit_tests.py
```

### 运行60小时测试

```bash
cd backend/scripts
python run_60_hour_tests.py
```

### 运行13小时测试（修复版）

```bash
cd backend/scripts
python run_13_hour_tests_fixed.py
```

### 验证测试修复

```bash
cd backend/scripts
python validate_test_fixes.py
```

### 重新分析协议

```bash
cd backend/scripts
python reanalyze_protocol.py
```

### 读取协议文档

```bash
cd backend/scripts
python read_protocol_doc.py
```

## ⚠️ 注意事项

1. **仅在开发时使用**：这些脚本主要用于开发和调试，生产环境不需要。

2. **需要设备连接**：大多数脚本需要设备已连接才能正常工作。

3. **查看依赖**：运行脚本前请确认所需的依赖库已安装。

4. **保存结果**：如果发现问题，建议保存诊断结果以便分析。

## 📊 脚本状态

| 脚本名称 | 状态 | 用途 |
|---------|------|------|
| check_modbus_client.py | ⚠️ 开发中 | Modbus客户端检查 |
| check_pymodbus_api.py | ⚠️ 开发中 | PyModbus API检查 |
| diagnose_power_supply.py | ⚠️ 开发中 | 电源设备诊断 |
| run_real_60_hour_tests.py | ⚠️ 开发中 | 真实60小时测试 |
| run_unit_tests.py | ⚠️ 开发中 | 单元测试 |
| run_60_hour_tests.py | ⚠️ 开发中 | 60小时测试 |
| run_13_hour_tests_fixed.py | ⚠️ 开发中 | 13小时测试（修复版） |
| validate_test_fixes.py | ⚠️ 开发中 | 验证测试修复 |
| reanalyze_protocol.py | ⚠️ 开发中 | 重新分析协议 |
| read_protocol_doc.py | ⚠️ 开发中 | 读取协议文档 |

## 🔧 维护说明

### 添加新脚本

1. 将脚本文件放入本目录
2. 更新本README文件
3. 添加使用说明
4. 更新脚本状态表

### 删除脚本

1. 确认脚本不再需要
2. 更新本README文件
3. 从脚本状态表中删除
4. 删除脚本文件

## 📞 技术支持

如果脚本运行出现问题，请：

1. 检查Python环境
2. 确认依赖库已安装
3. 查看错误日志
4. 联系开发团队

---

**创建日期**: 2026-06-02  
**维护者**: Industrial Automation Platform  
**状态**: 开发中