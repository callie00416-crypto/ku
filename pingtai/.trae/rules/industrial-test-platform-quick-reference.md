# 工业测试平台架构 - 快速参考

## 🚀 快速开始

### 标准架构流程

```
Driver → Action → Collector → Check → TestCase → Pytest
```

### 创建新测试的标准步骤

#### 1. 创建Driver（如果不存在）
```python
# drivers/device/{DEVICE}/{device}_driver.py
class ASDB2Driver(BaseDevice):
    def connect() -> bool
    def disconnect()
    def enable_servo(enable: bool) -> bool
    def set_speed(...) -> bool
    def read_feedback_speed() -> float
```

#### 2. 创建Action
```python
# actions/{device}_action.py
class MotorAction(BaseAction):
    def __init__(self, driver)
    def run_speed(rpm, direction, source) -> ActionResult
    def stop() -> ActionResult
    def read_speed() -> ActionResult
```

#### 3. 创建Collector（可选）
```python
# core/collectors/{metric}_collector.py
class SpeedCollector:
    def __init__(self, motor: MotorAction)
    def collect(duration, interval) -> List[Tuple[float, float]]
    def get_statistics(data) -> dict
```

#### 4. 创建Check
```python
# core/checks/{metric}_check.py
class SpeedCheck:
    @staticmethod
    def stable(actual, target, tolerance) -> bool
    @staticmethod
    def in_range(speed, min_speed, max_speed) -> bool
```

#### 5. 创建TestCase
```python
# core/testcase/{device}/{device}_{feature}_case.py
class ASDB2SpeedControlCase(BaseCase):
    def __init__(self, motor: MotorAction, case_data: Dict)
    def setup()
    def run()
```

#### 6. 创建Pytest TestCase
```python
# tests/{device}/test_{feature}.py
@pytest.fixture(scope="session")
def {device}_driver():
    driver = {Device}Driver(...)
    driver.connect()
    yield driver
    driver.disconnect()

@pytest.fixture
def {action}({device}_driver):
    {action} = {Action}({device}_driver)
    yield {action}
    {action}.stop()

@pytest.mark.parametrize("case_data", load_{feature}_cases())
def test_{feature}({action}, case_data):
    case = {Device}{Feature}Case({action}={action}, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

#### 7. 创建测试数据
```yaml
# data/{feature}.yaml
{feature}_cases:
  - case_id: "{feature}_{source}_{rpm}_{direction}"
    description: "描述"
    source: "P1-11"
    rpm: 1000
    direction: "CW"
    tolerance: 10.0
    settle_time: 5.0
```

## 📋 各层职责速查

| 层级 | 职责 | 可以调用 | 禁止调用 |
|------|------|---------|---------|
| **Driver** | 设备控制 | Protocol, Comm | 测试逻辑、业务逻辑、assert |
| **Action** | 业务动作封装 | Driver | Protocol, Comm、寄存器、assert |
| **Collector** | 数据采集 | Action | Driver、assert、测试逻辑 |
| **Check** | 断言 | 无 | Driver、测试逻辑、业务逻辑 |
| **TestCase** | 测试业务逻辑 | Action, Collector, Check | Driver, Protocol, Comm |
| **Pytest** | 测试执行 | TestCase, fixture | Driver, Protocol, Comm |

## 🚫 禁止事项速查

### ❌ 绝对禁止

```python
# ❌ 禁止1：在Driver中写测试逻辑
class ASDB2Driver(BaseDevice):
    def test_speed_control(self):  # ❌ 错误
        self.set_speed(p1_11=1000)
        assert abs(self.read_feedback_speed() - 1000) <= 10  # ❌ 错误

# ❌ 禁止2：在Action中直接操作寄存器
class MotorAction(BaseAction):
    def run_speed(self, rpm, direction, source):
        self.modbus.write_register(address=0x0218, value=0x0014)  # ❌ 错误

# ❌ 禁止3：在Action中使用assert
class MotorAction(BaseAction):
    def run_speed(self, rpm, direction, source):
        assert rpm >= 0 and rpm <= 3000  # ❌ 错误

# ❌ 禁止4：在TestCase中直接调用Driver
class ASDB2SpeedControlCase(BaseCase):
    def run(self):
        self.driver.set_speed(p1_11=1000)  # ❌ 错误
        self.driver.run_motor(1000, 'CW', 'P1-11')  # ❌ 错误

# ❌ 禁止5：在Pytest中直接使用Driver
def test_speed_control(driver):
    driver.set_speed(p1_11=1000)  # ❌ 错误
    driver.run_motor(1000, 'CW', 'P1-11')  # ❌ 错误
```

### ✅ 正确做法

```python
# ✅ 正确1：Driver只提供基础接口
class ASDB2Driver(BaseDevice):
    def set_speed(self, p1_09, p1_10, p1_11) -> bool:
        try:
            self.modbus.write_registers(...)
            return True
        except Exception as e:
            logger.error(f"设置速度失败: {e}")
            return False

# ✅ 正确2：Action封装业务逻辑
class MotorAction(BaseAction):
    def run_speed(self, rpm, direction, source) -> ActionResult:
        try:
            success = self.driver.run_motor(speed_rpm=rpm, direction=direction, source=source)
            if success:
                return ActionResult.success(message=f"电机运行: {rpm} RPM")
            else:
                return ActionResult.failed(f"电机运行失败")
        except Exception as e:
            return ActionResult.failed(f"运行电机异常: {str(e)}")

# ✅ 正确3：TestCase使用Action、Collector、Check
class ASDB2SpeedControlCase(BaseCase):
    def run(self):
        result = self.motor.initialize()
        assert result.is_success, f"初始化失败: {result.message}"
        
        result = self.motor.run_speed(1000, 'CW', 'P1-11')
        assert result.is_success, f"运行电机失败: {result.message}"
        
        result = self.motor.read_speed()
        speed = result.data.get('feedback_speed', 0.0)
        
        SpeedCheck.stable(speed, 1000, 10)

# ✅ 正确4：Pytest使用fixture和参数化
@pytest.mark.parametrize("case_data", load_speed_cases())
def test_speed_control(motor, case_data):
    case = ASDB2SpeedControlCase(motor=motor, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

## 🎯 常见模式

### 模式1：基本测试流程

```python
class ASDB2SpeedControlCase(BaseCase):
    def run(self):
        # 1. 初始化
        result = self.motor.initialize()
        assert result.is_success, f"初始化失败: {result.message}"
        
        # 2. 使能
        result = self.motor.enable_servo(True)
        assert result.is_success, f"使能失败: {result.message}"
        
        # 3. 运行
        result = self.motor.run_speed(1000, 'CW', 'P1-11')
        assert result.is_success, f"运行失败: {result.message}"
        
        # 4. 等待
        time.sleep(5.0)
        
        # 5. 读取
        result = self.motor.read_speed()
        speed = result.data.get('feedback_speed', 0.0)
        
        # 6. 检查
        SpeedCheck.stable(speed, 1000, 10)
        
        # 7. 采集
        data = self.collector.collect(duration=5, interval=0.1)
        
        # 8. 停止
        result = self.motor.stop()
        assert result.is_success, f"停止失败: {result.message}"
```

### 模式2：参数化测试

```python
@pytest.mark.parametrize("rpm,direction,tolerance", [
    (10, 'CW', 2.0),
    (100, 'CW', 5.0),
    (1000, 'CW', 10.0),
    (3000, 'CW', 30.0),
])
def test_speed_range(motor, rpm, direction, tolerance):
    result = motor.run_speed(rpm, direction, 'P1-11')
    assert result.is_success, f"运行失败: {result.message}"
    
    time.sleep(3.0)
    
    result = motor.read_speed()
    speed = result.data.get('feedback_speed', 0.0)
    
    SpeedCheck.stable(speed, rpm, tolerance)
    
    motor.stop()
```

### 模式3：数据驱动测试

```python
# data/speed.yaml
speed_cases:
  - case_id: "speed_p1_09_10_cw"
    rpm: 10
    direction: "CW"
    tolerance: 2.0

# tests/asdb2/test_speed_control.py
def load_speed_cases():
    with open('data/speed.yaml', 'r') as f:
        data = yaml.safe_load(f)
    return data.get('speed_cases', [])

@pytest.mark.parametrize("case_data", load_speed_cases())
def test_speed_control(motor, case_data):
    case = ASDB2SpeedControlCase(motor=motor, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

### 模式4：Fixture管理资源

```python
@pytest.fixture(scope="session")
def asdb2_driver():
    """Session级别：整个测试会话只创建一次"""
    driver = ASDB2Driver(...)
    driver.connect()
    yield driver
    driver.disconnect()

@pytest.fixture
def motor(asdb2_driver):
    """Function级别：每个测试函数都创建新的MotorAction"""
    motor = MotorAction(asdb2_driver)
    yield motor
    motor.stop()
```

## 📝 命名规范速查

### 文件命名

| 类型 | 命名规范 | 示例 |
|------|---------|------|
| Driver | `{device}_driver.py` | `asdb2_driver.py` |
| Action | `{device}_action.py` | `motor_action.py` |
| Check | `{metric}_check.py` | `speed_check.py` |
| Collector | `{metric}_collector.py` | `speed_collector.py` |
| TestCase | `{device}_{feature}_case.py` | `asdb2_speed_control_case.py` |
| Pytest | `test_{feature}.py` | `test_speed_control.py` |
| Data | `{feature}.yaml` | `speed.yaml` |

### 类命名

| 类型 | 命名规范 | 示例 |
|------|---------|------|
| Driver | `{Device}Driver` | `ASDB2Driver` |
| Action | `{Device}Action` | `MotorAction` |
| Check | `{Metric}Check` | `SpeedCheck` |
| Collector | `{Metric}Collector` | `SpeedCollector` |
| TestCase | `{Device}{Feature}Case` | `ASDB2SpeedControlCase` |
| Pytest | `Test{Device}{Feature}` | `TestASDB2SpeedControl` |

## 🔍 代码审查清单

### Driver层
- [ ] 不包含测试逻辑
- [ ] 不包含业务逻辑
- [ ] 不使用assert
- [ ] 不打印测试结果
- [ ] 只提供基础设备操作接口

### Action层
- [ ] 不直接操作寄存器
- [ ] 不关心通讯协议
- [ ] 不使用assert
- [ ] 不包含测试逻辑
- [ ] 返回ActionResult

### Collector层
- [ ] 不包含测试逻辑
- [ ] 不使用assert
- [ ] 不直接操作设备
- [ ] 返回结构化数据

### Check层
- [ ] 不包含测试逻辑
- [ ] 不直接操作设备
- [ ] 不包含业务逻辑
- [ ] 使用静态方法

### TestCase层
- [ ] 不直接操作寄存器
- [ ] 不关心通讯协议
- [ ] 不直接调用Driver方法
- [ ] 使用Action、Collector、Check
- [ ] 使用assert进行断言

### Pytest层
- [ ] 不直接操作寄存器
- [ ] 不关心通讯协议
- [ ] 不直接调用Driver方法
- [ ] 使用fixture管理资源
- [ ] 使用参数化测试

## 📚 完整文档

详细规范请参考：[industrial-test-platform-architecture.md](./industrial-test-platform-architecture.md)

## 🎯 核心原则

1. **分层清晰**：Driver → Action → Collector → Check → TestCase → Pytest
2. **解耦彻底**：不跨层调用
3. **复用性强**：Action、Check、Collector可复用
4. **工业级稳定性**：支持回滚、错误恢复、日志记录

**遵循此架构，可以确保代码的一致性、可维护性和可扩展性。**