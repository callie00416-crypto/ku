# 编码器上断电测试参数说明

## 一、参数总览

| 参数名 | 类型 | 默认值 | 适用用例 | 说明 |
|--------|------|--------|----------|------|
| `cycle_count` | int | 10 | PowerCycle, Waveform | 循环测试次数 |
| `power_off_delay` | float | 1.0 | 全部 | 断电持续时间(秒) |
| `power_on_delay` | float | 2.0 | 全部 | 上电稳定时间(秒) |
| `tolerance` | float | 0.5 | 全部 | 角度偏差容忍度(度) |
| `waveform_type` | str | "SIN" | PowerCycle, Waveform | 波形类型 |
| `frequency` | float | 1000.0 | PowerCycle, Waveform | 波形频率(Hz) |
| `amplitude` | float | 5.0 | PowerCycle, Waveform | 波形幅度(Vpp) |
| `gain` | int | 20 | 全部 | 功率放大器增益(dB) |

---

## 二、参数详细说明

### 1. cycle_count

**类型**：int  
**默认值**：10  
**适用用例**：EncoderPowerCycleCase, EncoderWaveformPowerCycleCase  
**说明**：上断电循环测试的总次数。每次循环包含：断电 → 等待 → 上电 → 等待 → 验证  

**取值建议**：
- 常规测试：10-20次
- 稳定性测试：50-100次
- 快速验证：3-5次

---

### 2. power_off_delay

**类型**：float  
**默认值**：1.0  
**适用用例**：全部  
**说明**：功率放大器关闭输出后的等待时间，确保编码器完全断电  

**取值依据**：
- 考虑编码器电源电容放电时间
- 典型值：1-2秒
- 如需确保完全放电可设置更长时间

---

### 3. power_on_delay

**类型**：float  
**默认值**：2.0  
**适用用例**：全部  
**说明**：功率放大器打开输出后的等待时间，确保编码器完成上电初始化  

**取值依据**：
- 编码器启动时间（通常100ms-1s）
- 通信建立时间
- 数据稳定时间
- 建议设置为2-3秒以确保稳定

---

### 4. tolerance

**类型**：float  
**默认值**：0.5  
**适用用例**：全部  
**说明**：断电前后角度允许的最大偏差（单位：度）  

**验收标准**：
- 高精度编码器：≤ 0.1°
- 普通编码器：≤ 0.5°
- 最大容忍：≤ 1.0°

**断言逻辑**：
```python
assert angle_diff <= tolerance, \
    f"角度偏差 {angle_diff:.4f}° 超过容忍度 {tolerance}°"
```

---

### 5. waveform_type

**类型**：str  
**默认值**："SIN"  
**适用用例**：EncoderPowerCycleCase, EncoderWaveformPowerCycleCase  
**说明**：波形发生器输出的波形类型  

**支持值**：
| 值 | 波形类型 | 说明 |
|----|----------|------|
| "SIN" | 正弦波 | 最常用，模拟交流信号 |
| "SQU" | 方波 | 数字信号测试 |
| "TRI" | 三角波 | 线性变化信号 |
| "RAMP" | 锯齿波 | 单向斜坡 |
| "PULS" | 脉冲 | 脉冲信号 |
| "NOIS" | 噪声 | 随机噪声 |

---

### 6. frequency

**类型**：float  
**默认值**：1000.0  
**适用用例**：EncoderPowerCycleCase, EncoderWaveformPowerCycleCase  
**说明**：波形发生器输出频率（单位：Hz）  

**取值范围**：
- 最小值：1μHz（0.000001Hz）
- 最大值：25MHz（受限于DG811硬件）

**典型应用**：
- 低频测试：50-100Hz
- 中频测试：1kHz-10kHz
- 高频测试：100kHz-1MHz

---

### 7. amplitude

**类型**：float  
**默认值**：5.0  
**适用用例**：EncoderPowerCycleCase, EncoderWaveformPowerCycleCase  
**说明**：波形发生器输出幅度（单位：Vpp，峰峰值）  

**取值范围**：
- 最小值：0.01Vpp（10mV）
- 最大值：20Vpp（受限于DG811硬件）

**注意事项**：
- 需配合功率放大器增益使用
- 实际输出 = 波形幅度 × 放大倍数
- 确保不超过编码器输入范围

---

### 8. gain

**类型**：int  
**默认值**：20  
**适用用例**：全部  
**说明**：功率放大器增益（单位：dB）  

**支持值**：
| 值 | 说明 | 放大倍数 |
|----|------|----------|
| 0 | 无放大 | 1x |
| 12 | 低增益 | ~3.98x |
| 20 | 标准增益 | ~10x |

**计算公式**：
```
放大倍数 = 10^(gain/20)
例如：20dB = 10^(20/20) = 10x
```

---

## 三、参数配置示例

### 示例1：常规上断电测试

```python
case = EncoderPowerCycleCase(
    power_amplifier=power_amp,
    encoder=encoder
)

# 使用默认参数
case.set_parameter('cycle_count', 10)
case.set_parameter('tolerance', 0.5)
```

### 示例2：带波形激励测试

```python
case = EncoderWaveformPowerCycleCase(
    power_amplifier=power_amp,
    waveform_generator=waveform_gen,
    encoder=encoder
)

case.set_parameter('cycle_count', 5)
case.set_parameter('waveform_type', 'SIN')
case.set_parameter('frequency', 1000.0)
case.set_parameter('amplitude', 5.0)
case.set_parameter('gain', 20)
```

### 示例3：严格精度测试

```python
case = EncoderSinglePowerCycleCase(
    power_amplifier=power_amp,
    encoder=encoder
)

case.set_parameter('power_off_delay', 2.0)
case.set_parameter('power_on_delay', 3.0)
case.set_parameter('tolerance', 0.1)  # 高精度要求
```

---

## 四、参数依赖关系

```
波形发生器设置
    │
    ├── waveform_type → 波形类型选择
    ├── frequency     → 配合波形类型使用
    └── amplitude     → 与功率放大器增益配合
            │
            ▼
功率放大器设置
    │
    └── gain → 决定最终输出幅度
            │
            ▼
编码器测试
    │
    ├── cycle_count      → 测试次数
    ├── power_off_delay  → 断电等待时间
    ├── power_on_delay   → 上电等待时间
    └── tolerance        → 验收标准
```

---

## 五、参数校验规则

| 参数 | 校验规则 | 异常处理 |
|------|----------|----------|
| `cycle_count` | > 0 | 断言失败 |
| `power_off_delay` | ≥ 0 | 设置为默认值 |
| `power_on_delay` | ≥ 0.5 | 设置为最小值 |
| `tolerance` | > 0 | 断言失败 |
| `waveform_type` | 有效值列表 | 抛出异常 |
| `frequency` | 1μHz ~ 25MHz | 抛出异常 |
| `amplitude` | 0.01 ~ 20Vpp | 抛出异常 |
| `gain` | 0, 12, 20 | 断言失败 |

---

## 六、典型测试场景参数配置

| 场景 | cycle_count | power_off_delay | power_on_delay | tolerance | waveform_type | frequency | amplitude | gain |
|------|------------|----------------|---------------|-----------|---------------|-----------|-----------|------|
| 快速验证 | 3 | 1.0 | 2.0 | 1.0 | SIN | 1000 | 5.0 | 20 |
| 常规测试 | 10 | 1.0 | 2.0 | 0.5 | SIN | 1000 | 5.0 | 20 |
| 稳定性测试 | 50 | 1.0 | 2.0 | 0.5 | SIN | 1000 | 5.0 | 20 |
| 高精度测试 | 10 | 2.0 | 3.0 | 0.1 | SIN | 1000 | 5.0 | 20 |
| 波形响应测试 | 5 | 1.0 | 2.0 | 0.5 | SQU | 10000 | 3.0 | 12 |