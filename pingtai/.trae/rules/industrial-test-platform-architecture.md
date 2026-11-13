# 工业测试平台架构规范

## 📋 概述

本文档定义了工业测试平台的架构规范，所有开发必须严格遵守。

**核心原则**：
- 分层清晰，职责明确
- 解耦彻底，不跨层调用
- 复用性强，易于扩展
- 工业级稳定性

## 🏗️ 架构分层

### 标准架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Pytest TestCase    - 测试用例执行层                                        │
│      ↓ 使用                                                                │
│  TestCase           - 测试业务逻辑层                                       │
│      ↓ 使用                                                                │
│  Action             - 业务动作封装层                                       │
│      ↓ 调用                                                                │
│  Driver             - 设备驱动层                                           │
│      ↓ 使用                                                                │
│  Protocol           - 协议封装层                                           │
│      ↓ 使用                                                                │
│  Comm               - 通讯传输层                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Check              - 断言层                                                │
│      ↓ 断言                                                                │
│  TestCase           - 测试业务逻辑层                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Collector          - 数据采集层                                            │
│      ↓ 采集                                                                │
│  TestCase           - 测试业务逻辑层                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Data (YAML)        - 测试数据层                                            │
│      ↓ 加载                                                                │
│  Pytest TestCase    - 测试用例执行层                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 目录结构规范

```
backend/projects/encoder_test/
├── actions/                          # Action层 - 业务动作封装
│   ├── base/                         # 基础Action
│   │   ├── base_action.py           # BaseAction基类
│   │   ├── action_result.py         # ActionResult结果类
│   │   └── action_context.py        # ActionContext上下文类
│   ├── motor_action.py              # 电机动作
│   ├── encoder_action.py            # 编码器动作
│   ├── power_action.py              # 电源动作
│   └── common/                       # 通用动作
│
├── core/                             # 核心层
│   ├── checks/                       # Check层 - 断言层
│   │   ├── __init__.py
│   │   ├── speed_check.py           # 速度断言
│   │   ├── position_check.py        # 位置断言
│   │   └── alarm_check.py           # 报警断言
│   ├── collectors/                   # Collector层 - 数据采集层
│   │   ├── __init__.py
│   │   ├── speed_collector.py       # 速度数据采集
│   │   ├── position_collector.py    # 位置数据采集
│   │   └── alarm_collector.py       # 报警数据采集
│   └── testcase/                     # TestCase层 - 测试业务逻辑层
│       ├── base/                     # 基础TestCase
│       │   ├── base_case.py         # BaseCase基类
│       │   ├── case_result.py       # CaseResult结果类
│       │   └── case_context.py      # CaseContext上下文类
│       ├── asdb2/                    # ASDB2测试用例
│       │   ├── __init__.py
│       │   └── asdb2_speed_control_case.py
│       └── encoder/                  # 编码器测试用例
│           ├── __init__.py
│           └── encoder_accuracy_case.py
│
├── data/                             # Data层 - 测试数据层
│   ├── speed.yaml                    # 速度测试数据
│   ├── position.yaml                 # 位置测试数据
│   └── power_cycle.yaml              # 上断电测试数据
│
├── tests/                            # Pytest TestCase层 - 测试用例执行层
│   ├── asdb2/                        # ASDB2测试
│   │   ├── __init__.py
│   │   └── test_speed_control.py    # 速度控制测试
│   └── encoder/                      # 编码器测试
│       ├── __init__.py
│       └── test_accuracy.py         # 精度测试
│
├── drivers/                          # Driver层 - 设备驱动层
│   └── device/
│       ├── ASDB2/
│       │   ├── asdb2_driver.py       # ASDB2驱动器
│       │   └── tests/                # 驱动层测试
│       └── encoder/
│           ├── dpt_encoder.py        # DPT编码器驱动
│           └── tests/                # 驱动层测试
│
├── conftest.py                       # Pytest配置文件
└── examples/                         # 运行示例
    └── asdb2_speed_control_example.py
```

## 📐 各层职责规范

### 1. Driver层（设备驱动层）

**职责**：
- 只负责设备控制
- 提供基础的设备操作接口
- 不写测试逻辑
- 不包含业务逻辑

**接口规范**：
```python
class ASDB2Driver(BaseDevice):
    # 连接管理
    def connect() -> bool
    def disconnect()
    
    # 设备控制
    def enable_servo(enable: bool) -> bool
    def disable_servo() -> bool
    def set_speed(p1_09, p1_10, p1_11) -> bool
    def read_feedback_speed() -> float
    def run_motor(speed_rpm, direction, source) -> bool
    def stop_motor() -> bool
    def initialize_driver() -> bool
    
    # 数据读写
    def read_data() -> Dict[str, Any]
    def write_data(data: Dict[str, Any]) -> bool
    
    # 状态管理
    def reset()
    def is_connected -> bool
```

**禁止事项**：
- ❌ 禁止在Driver中写测试逻辑
- ❌ 禁止在Driver中包含业务逻辑
- ❌ 禁止在Driver中直接使用assert
- ❌ 禁止在Driver中打印测试结果

**正确示例**：
```python
class ASDB2Driver(BaseDevice):
    def set_speed(self, p1_09=None, p1_10=None, p1_11=None) -> bool:
        """设置速度值"""
        try:
            if p1_09 is not None:
                value = int(p1_09 * 10)
                self.modbus.write_registers(...)
            return True
        except Exception as e:
            logger.error(f"设置速度失败: {e}")
            return False
```

**错误示例**：
```python
class ASDB2Driver(BaseDevice):
    def test_speed_control(self):
        """❌ 错误：Driver中不应包含测试逻辑"""
        self.set_speed(p1_11=1000)
        time.sleep(5)
        speed = self.read_feedback_speed()
        assert abs(speed - 1000) <= 10  # ❌ 错误：不应使用assert
```

### 2. Action层（业务动作封装层）

**职责**：
- 封装业务动作
- 隐藏底层寄存器和协议细节
- 提供业务级别的动作接口
- 返回ActionResult

**接口规范**：
```python
class MotorAction(BaseAction):
    def __init__(self, driver)
    
    # 业务动作
    def enable_servo(enable: bool) -> ActionResult
    def run_speed(rpm, direction, source) -> ActionResult
    def stop() -> ActionResult
    def read_speed() -> ActionResult
    def set_speed(p1_09, p1_10, p1_11) -> ActionResult
    def initialize() -> ActionResult
    
    # 继承BaseAction
    def execute() -> ActionResult
    def run() -> ActionResult
```

**禁止事项**：
- ❌ 禁止在Action中直接操作寄存器
- ❌ 禁止在Action中关心通讯协议
- ❌ 禁止在Action中使用assert
- ❌ 禁止在Action中包含测试逻辑

**正确示例**：
```python
class MotorAction(BaseAction):
    def run_speed(self, rpm: float, direction: str = 'CW', source: str = 'P1-11') -> ActionResult:
        """运行电机"""
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("电机未连接")
            
            success = self.driver.run_motor(speed_rpm=rpm, direction=direction, source=source)
            if success:
                return ActionResult.success(
                    message=f"电机运行: {rpm} RPM, {direction}, {source}",
                    data={'speed_rpm': rpm, 'direction': direction, 'source': source}
                )
            else:
                return ActionResult.failed(f"电机运行失败: {rpm} RPM")
        except Exception as e:
            return ActionResult.failed(f"运行电机异常: {str(e)}", error_detail=str(e))
```

**错误示例**：
```python
class MotorAction(BaseAction):
    def run_speed(self, rpm, direction, source):
        """❌ 错误：直接操作寄存器"""
        self.modbus.write_register(address=0x0218, value=0x0014)  # ❌ 错误
        self.modbus.write_register(address=0x021A, value=0x0015)  # ❌ 错误
        
        """❌ 错误：使用assert"""
        assert rpm >= 0 and rpm <= 3000  # ❌ 错误
```

### 3. Collector层（数据采集层）

**职责**：
- 采集测试数据
- 支持连续采样
- 返回结构化数据
- 提供统计分析

**接口规范**：
```python
class SpeedCollector:
    def __init__(self, motor: MotorAction)
    
    # 数据采集
    def collect(duration: float, interval: float) -> List[Tuple[float, float]]
    def collect_single() -> Optional[float]
    
    # 统计分析
    def get_statistics(data: List[Tuple[float, float]]) -> dict
```

**禁止事项**：
- ❌ 禁止在Collector中包含测试逻辑
- ❌ 禁止在Collector中使用assert
- ❌ 禁止在Collector中直接操作设备

**正确示例**：
```python
class SpeedCollector:
    def collect(self, duration: float = 10.0, interval: float = 0.1) -> List[Tuple[float, float]]:
        """采集速度数据"""
        data = []
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time:
            current_time = time.time()
            result = self.motor.read_speed()
            if result.is_success:
                speed = result.data.get('feedback_speed', 0.0)
                data.append((current_time - start_time, speed))
            
            elapsed = time.time() - current_time
            if elapsed < interval:
                time.sleep(interval - elapsed)
        
        return data
```

### 4. Check层（断言层）

**职责**：
- 提供断言方法
- 支持容忍度配置
- 提供清晰的断言消息
- 使用静态方法

**接口规范**：
```python
class SpeedCheck:
    @staticmethod
    def stable(actual: float, target: float, tolerance: float) -> bool
    
    @staticmethod
    def in_range(speed: float, min_speed: float, max_speed: float) -> bool
    
    @staticmethod
    def zero(speed: float, tolerance: float) -> bool
    
    @staticmethod
    def direction_match(speed: float, direction: str) -> bool
```

**禁止事项**：
- ❌ 禁止在Check中包含测试逻辑
- ❌ 禁止在Check中直接操作设备
- ❌ 禁止在Check中包含业务逻辑

**正确示例**：
```python
class SpeedCheck:
    @staticmethod
    def stable(actual: float, target: float, tolerance: float = 5.0) -> bool:
        """检查速度是否稳定"""
        error = abs(actual - target)
        passed = error <= tolerance
        
        if not passed:
            raise AssertionError(
                f"速度不稳定: 实际={actual} RPM, 目标={target} RPM, "
                f"误差={error} RPM, 容忍度={tolerance} RPM"
            )
        
        logger.info(f"速度稳定: {actual} RPM (目标={target} RPM, 误差={error} RPM)")
        return True
```

### 5. TestCase层（测试业务逻辑层）

**职责**：
- 真正的测试逻辑
- 使用Action、Collector、Check
- 不直接操作寄存器
- 不关心通讯协议
- 使用assert进行断言

**接口规范**：
```python
class ASDB2SpeedControlCase(BaseCase):
    def __init__(self, motor: MotorAction, case_data: Dict[str, Any])
    
    # 测试流程
    def setup()
    def run()
    
    # 继承BaseCase
    def execute() -> CaseResult
```

**禁止事项**：
- ❌ 禁止在TestCase中直接操作寄存器
- ❌ 禁止在TestCase中关心通讯协议
- ❌ 禁止在TestCase中直接调用Driver方法（应通过Action）

**正确示例**：
```python
class ASDB2SpeedControlCase(BaseCase):
    def run(self):
        # 1. 初始化
        result = self.motor.initialize()
        assert result.is_success, f"初始化失败: {result.message}"
        
        # 2. 使能伺服
        result = self.motor.enable_servo(True)
        assert result.is_success, f"使能伺服失败: {result.message}"
        
        # 3. 运行电机
        result = self.motor.run_speed(1000, 'CW', 'P1-11')
        assert result.is_success, f"运行电机失败: {result.message}"
        
        # 4. 读取速度
        result = self.motor.read_speed()
        speed = result.data.get('feedback_speed', 0.0)
        
        # 5. 检查速度
        SpeedCheck.stable(speed, 1000, 10)
        
        # 6. 采集数据
        data = self.collector.collect(duration=5, interval=0.1)
        
        # 7. 停止电机
        result = self.motor.stop()
        assert result.is_success, f"停止电机失败: {result.message}"
```

**错误示例**：
```python
class ASDB2SpeedControlCase(BaseCase):
    def run(self):
        """❌ 错误：直接调用Driver方法"""
        self.driver.set_speed(p1_11=1000)  # ❌ 错误
        
        """❌ 错误：直接操作寄存器"""
        self.driver.modbus.write_register(...)  # ❌ 错误
        
        """❌ 错误：关心通讯协议"""
        self.driver.protocol.send(...)  # ❌ 错误
```

### 6. Pytest TestCase层（测试用例执行层）

**职责**：
- 使用pytest框架执行测试
- 使用fixture管理资源
- 使用参数化测试
- 支持数据驱动测试

**接口规范**：
```python
@pytest.fixture(scope="session")
def asdb2_driver():
    """Session级别fixture"""
    driver = ASDB2Driver(...)
    driver.connect()
    yield driver
    driver.disconnect()

@pytest.fixture
def motor(asdb2_driver):
    """Function级别fixture"""
    motor = MotorAction(asdb2_driver)
    yield motor
    motor.stop()

@pytest.mark.parametrize("case_data", load_speed_cases())
def test_speed_control(motor, case_data):
    """参数化测试"""
    case = ASDB2SpeedControlCase(motor=motor, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

**禁止事项**：
- ❌ 禁止在pytest测试中直接操作寄存器
- ❌ 禁止在pytest测试中关心通讯协议
- ❌ 禁止在pytest测试中直接调用Driver方法

**正确示例**：
```python
@pytest.mark.parametrize("case_data", load_speed_cases())
def test_speed_control(motor, case_data):
    """✅ 正确：使用MotorAction"""
    case = ASDB2SpeedControlCase(motor=motor, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

**错误示例**：
```python
def test_speed_control(driver):
    """❌ 错误：直接使用Driver"""
    driver.set_speed(p1_11=1000)  # ❌ 错误
    driver.run_motor(1000, 'CW', 'P1-11')  # ❌ 错误
    speed = driver.read_feedback_speed()  # ❌ 错误
    assert abs(speed - 1000) <= 10  # ❌ 错误
```

### 7. Data层（测试数据层）

**职责**：
- 分离测试数据
- 使用YAML格式
- 方便测试人员维护

**格式规范**：
```yaml
speed_cases:
  - case_id: "speed_p1_09_10_cw"
    description: "P1-09低速测试 - 10RPM 顺时针"
    source: "P1-09"
    rpm: 10
    direction: "CW"
    tolerance: 2.0
    settle_time: 3.0
```

**禁止事项**：
- ❌ 禁止在数据文件中包含逻辑
- ❌ 禁止在数据文件中使用Python代码

## 🚫 禁止事项总结

### 跨层调用禁止

| 层级 | 可以调用 | 禁止调用 |
|------|---------|---------|
| Pytest TestCase | TestCase, fixture | Driver, Protocol, Comm |
| TestCase | Action, Collector, Check | Driver, Protocol, Comm |
| Action | Driver | Protocol, Comm |
| Driver | Protocol, Comm | 无 |
| Protocol | Comm | 无 |
| Comm | 无 | 无 |

### 代码禁止

| 层级 | 禁止事项 |
|------|---------|
| Driver | 测试逻辑、业务逻辑、assert、打印测试结果 |
| Action | 直接操作寄存器、关心通讯协议、assert、测试逻辑 |
| Collector | 测试逻辑、assert、直接操作设备 |
| Check | 测试逻辑、直接操作设备、业务逻辑 |
| TestCase | 直接操作寄存器、关心通讯协议、直接调用Driver |
| Pytest TestCase | 直接操作寄存器、关心通讯协议、直接调用Driver |

## ✅ 最佳实践

### 1. 使用Fixture管理资源

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

### 2. 使用参数化测试

```python
@pytest.mark.parametrize("case_data", load_speed_cases())
def test_speed_control(motor, case_data):
    case = ASDB2SpeedControlCase(motor=motor, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

### 3. 使用数据驱动测试

```yaml
# data/speed.yaml
speed_cases:
  - case_id: "speed_p1_09_10_cw"
    source: "P1-09"
    rpm: 10
    direction: "CW"
```

```python
def load_speed_cases():
    with open('data/speed.yaml', 'r') as f:
        data = yaml.safe_load(f)
    return data.get('speed_cases', [])
```

### 4. 使用Check进行断言

```python
# ✅ 正确
SpeedCheck.stable(actual=998, target=1000, tolerance=5)

# ❌ 错误
assert abs(998 - 1000) <= 5
```

### 5. 使用Collector采集数据

```python
# ✅ 正确
collector = SpeedCollector(motor)
data = collector.collect(duration=10, interval=0.1)
stats = collector.get_statistics(data)

# ❌ 错误
speeds = []
for _ in range(100):
    speed = driver.read_feedback_speed()
    speeds.append(speed)
    time.sleep(0.1)
```

### 6. 使用Action封装业务逻辑

```python
# ✅ 正确
motor.run_speed(1000, 'CW', 'P1-11')

# ❌ 错误
driver.set_speed(p1_11=1000)
driver.select_speed_source('P1-11')
driver.set_direction('CW')
driver.enable_servo(True)
```

## 📝 命名规范

### 文件命名

| 层级 | 命名规范 | 示例 |
|------|---------|------|
| Driver | `{device}_driver.py` | `asdb2_driver.py` |
| Action | `{device}_action.py` | `motor_action.py` |
| Check | `{metric}_check.py` | `speed_check.py` |
| Collector | `{metric}_collector.py` | `speed_collector.py` |
| TestCase | `{device}_{feature}_case.py` | `asdb2_speed_control_case.py` |
| Pytest TestCase | `test_{feature}.py` | `test_speed_control.py` |
| Data | `{feature}.yaml` | `speed.yaml` |

### 类命名

| 层级 | 命名规范 | 示例 |
|------|---------|------|
| Driver | `{Device}Driver` | `ASDB2Driver` |
| Action | `{Device}Action` | `MotorAction` |
| Check | `{Metric}Check` | `SpeedCheck` |
| Collector | `{Metric}Collector` | `SpeedCollector` |
| TestCase | `{Device}{Feature}Case` | `ASDB2SpeedControlCase` |
| Pytest TestCase | `Test{Device}{Feature}` | `TestASDB2SpeedControl` |

### 方法命名

| 层级 | 命名规范 | 示例 |
|------|---------|------|
| Driver | 动词或动词短语 | `connect()`, `set_speed()` |
| Action | 动词或动词短语 | `run_speed()`, `stop()` |
| Check | 动词或形容词 | `stable()`, `in_range()` |
| Collector | 动词或动词短语 | `collect()`, `get_statistics()` |
| TestCase | 动词或动词短语 | `setup()`, `run()` |
| Pytest TestCase | `test_{feature}` | `test_speed_control()` |

## 🔍 代码审查清单

### Driver层审查

- [ ] 不包含测试逻辑
- [ ] 不包含业务逻辑
- [ ] 不使用assert
- [ ] 不打印测试结果
- [ ] 只提供基础设备操作接口

### Action层审查

- [ ] 不直接操作寄存器
- [ ] 不关心通讯协议
- [ ] 不使用assert
- [ ] 不包含测试逻辑
- [ ] 返回ActionResult

### Collector层审查

- [ ] 不包含测试逻辑
- [ ] 不使用assert
- [ ] 不直接操作设备
- [ ] 返回结构化数据

### Check层审查

- [ ] 不包含测试逻辑
- [ ] 不直接操作设备
- [ ] 不包含业务逻辑
- [ ] 使用静态方法

### TestCase层审查

- [ ] 不直接操作寄存器
- [ ] 不关心通讯协议
- [ ] 不直接调用Driver方法
- [ ] 使用Action、Collector、Check
- [ ] 使用assert进行断言

### Pytest TestCase层审查

- [ ] 不直接操作寄存器
- [ ] 不关心通讯协议
- [ ] 不直接调用Driver方法
- [ ] 使用fixture管理资源
- [ ] 使用参数化测试

## 📚 参考资料

- [ASDB2架构文档](../backend/projects/encoder_test/ASDB2_ARCHITECTURE.md)
- [导入规范](./encoder_test_import_rules.md)
- [命名规范](./naming.md)
- [工业设备生命周期规范](./industrial-device-lifecycle-specification.md)

## 🎯 总结

**核心原则**：
1. 分层清晰，职责明确
2. 解耦彻底，不跨层调用
3. 复用性强，易于扩展
4. 工业级稳定性

**架构流程**：
```
Driver → Action → Collector → Check → TestCase → Pytest
```

**禁止事项**：
- 禁止跨层调用
- 禁止在Driver中写测试逻辑
- 禁止在Action中直接操作寄存器
- 禁止在TestCase中直接调用Driver

**最佳实践**：
- 使用Fixture管理资源
- 使用参数化测试
- 使用数据驱动测试
- 使用Check进行断言
- 使用Collector采集数据
- 使用Action封装业务逻辑

**遵循此规范，可以确保代码的一致性、可维护性和可扩展性。**