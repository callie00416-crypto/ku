# encoder_test 项目目录结构规范

## 目录结构

```
encoder_test/
├── actions/           # Action层（业务动作封装）
├── core/              # 核心功能
│   ├── checks/        # Check层（断言方法）
│   ├── collectors/    # Collector层（数据采集）
│   ├── testcase/      # TestCase层（测试用例业务逻辑）
│   └── test_engine/   # 测试引擎（任务调度）
├── drivers/           # Driver层（设备驱动）
├── data/              # 数据层（YAML测试数据）
├── tests/             # Pytest测试用例（测试执行层）
└── utils/             # 工具函数
```

## core/testcase vs tests 目录区别

### 1. `core/testcase` - TestCase层（业务逻辑层）

**职责**：
- 定义测试用例的业务逻辑
- 封装测试步骤和流程
- 提供可复用的测试用例类

**特点**：
- 继承自`BaseCase`
- 使用Action、Collector、Check层
- 不直接运行，需要被测试框架调用
- 可以被不同的测试框架调用（pytest、unittest等）

**示例**：
```python
# core/testcase/encoder/encoder_power_cycle_case.py
class EncoderPowerCycleCase(BaseCase):
    """编码器上断电测试用例"""
    
    def run(self):
        # 1. 初始化驱动器
        # 2. 使能伺服
        # 3. 设置速度
        # 4. 运行电机
        # 5. 检查速度稳定性
        # 6. 停止电机
```

### 2. `tests` - Pytest测试用例（执行层）

**职责**：
- 使用pytest框架执行测试用例
- 管理测试资源（fixture）
- 实现参数化测试
- 生成测试报告

**特点**：
- 使用pytest fixture管理资源
- 使用pytest.mark.parametrize实现参数化测试
- 可以直接运行：`pytest tests/asdb2/test_speed_control.py -v`
- 调用`core/testcase`中的测试用例类

**示例**：
```python
# tests/encoder/test_power_cycle.py
@pytest.fixture
def encoder(encoder_driver):
    """编码器Fixture"""
    encoder_action = EncoderAction(encoder_driver)
    yield encoder_action
    encoder_action.stop()

@pytest.mark.parametrize("cycles", [10, 50, 100])
def test_power_cycle(encoder, cycles):
    """测试上断电循环"""
    case = EncoderPowerCycleCase(
        encoder_action=encoder,
        case_data={'cycle_count': cycles}
    )
    result = case.execute()
    assert result.status.value == 'passed'
```

## 使用方式

### 推荐的使用流程

```
1. 在 core/testcase/ 中定义测试用例类
   ↓
2. 在 tests/ 中创建pytest测试用例
   ↓
3. 使用pytest运行测试
```

### 具体示例

#### 步骤1：在`core/testcase/`中定义测试用例类
```python
# core/testcase/encoder/encoder_power_cycle_case.py
class EncoderPowerCycleCase(BaseCase):
    """编码器上断电测试用例"""
    
    def run(self):
        # 使用Action层
        result = self._encoder.read_both_angles()
        
        # 使用Check层
        AngleCheck.stable(angle, target, tolerance)
```

#### 步骤2：在`tests/`中创建pytest测试用例
```python
# tests/encoder/test_power_cycle.py
@pytest.fixture
def encoder(encoder_driver):
    """编码器Fixture"""
    encoder_action = EncoderAction(encoder_driver)
    yield encoder_action

@pytest.mark.parametrize("cycles", [10, 50, 100])
def test_power_cycle(encoder, cycles):
    """测试上断电循环"""
    case = EncoderPowerCycleCase(
        encoder_action=encoder,
        case_data={'cycle_count': cycles}
    )
    result = case.execute()
    assert result.status.value == 'passed'
```

#### 步骤3：使用pytest运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/encoder/test_power_cycle.py -v

# 运行特定参数
pytest tests/encoder/test_power_cycle.py::test_power_cycle -k "cycles-50"
```

## 架构优势

### 1. 分层清晰
```
TestCase层（业务逻辑）
    ↓ 被调用
Pytest层（测试执行）
```

### 2. 复用性强
- 同一个TestCase可以被多个测试框架调用
- 同一个TestCase可以用于单元测试、集成测试、系统测试

### 3. 灵活性高
- 可以使用不同的测试框架（pytest、unittest、nose）
- 可以轻松切换测试数据源（YAML、JSON、数据库）

### 4. 维护性好
- 业务逻辑集中在TestCase层
- 测试执行集中在Pytest层
- 修改业务逻辑不影响测试执行

## 对比总结

| 特性 | core/testcase | tests |
|------|---------------|-------|
| 职责 | 定义测试业务逻辑 | 执行测试用例 |
| 继承 | BaseCase | pytest.TestCase |
| 使用 | Action、Collector、Check | pytest fixture |
| 运行 | 不直接运行 | 直接运行 |
| 复用 | 可被多个框架调用 | 调用TestCase |
| 位置 | core/testcase/ | tests/ |

## 最佳实践

### 1. 在`core/testcase/`中定义测试用例类
- 继承自`BaseCase`
- 使用Action、Collector、Check层
- 不直接操作Driver
- 不关心测试框架

### 2. 在`tests/`中创建pytest测试用例
- 使用pytest fixture管理资源
- 使用pytest.mark.parametrize实现参数化测试
- 调用`core/testcase`中的测试用例类
- 使用pytest断言

### 3. 使用fixture管理测试资源
```python
@pytest.fixture(scope="session")
def driver():
    """Session级别fixture - 整个测试会话只创建一次"""
    driver = create_driver()
    driver.connect()
    yield driver
    driver.disconnect()

@pytest.fixture
def motor(driver):
    """Function级别fixture - 每个测试函数都会创建新的实例"""
    motor = MotorAction(driver)
    yield motor
    motor.stop()
```

### 4. 使用参数化测试
```python
@pytest.mark.parametrize("rpm", [10, 100, 1000, 3000])
def test_speed_control(motor, rpm):
    """测试速度控制 - 参数化测试"""
    motor.set_speed(p1_11=rpm)
    motor.run_speed(rpm, 'CW', 'P1-11')
    # ... 测试逻辑
```

### 5. 使用数据驱动测试
```python
def load_test_cases():
    """从YAML文件加载测试用例"""
    yaml_file = Path(__file__).parent.parent / 'data' / 'test_cases.yaml'
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('test_cases', [])

@pytest.mark.parametrize("case_data", load_test_cases())
def test_cases(motor, case_data):
    """数据驱动测试"""
    case = TestCase(motor=motor, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

## 目录命名规范

### core/testcase/ 目录结构
```
core/testcase/
├── base/              # 基础测试用例
│   ├── base_case.py   # BaseCase基类
│   ├── case_context.py
│   ├── case_result.py
│   └── config.py
├── encoder/           # 编码器测试用例
│   ├── encoder_power_cycle_case.py
│   └── encoder_angle_test_case.py
├── asdb2/             # ASDB2测试用例
│   └── asdb2_speed_control_case.py
└── tests/             # 测试用例测试（可选）
    └── test_cases.py
```

### tests/ 目录结构
```
tests/
├── encoder/           # 编码器测试
│   ├── test_power_cycle.py
│   └── test_angle_test.py
├── asdb2/             # ASDB2测试
│   └── test_speed_control.py
├── conftest.py        # pytest配置和fixture
└── __init__.py
```

## 总结

**核心原则**：
1. **core/testcase/** - 定义测试业务逻辑，不关心测试框架
2. **tests/** - 使用pytest执行测试，管理测试资源
3. **分层清晰** - TestCase层和Pytest层职责明确
4. **复用性强** - 同一个TestCase可以被多个测试框架调用

**最佳实践**：
- 在`core/testcase/`中定义可复用的测试用例类
- 在`tests/`中创建pytest测试用例来执行测试
- 使用fixture管理测试资源
- 使用参数化测试实现数据驱动测试