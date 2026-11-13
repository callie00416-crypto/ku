# ASDB2工业测试平台架构说明

## 架构概览

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

## 目录结构

```
backend/projects/encoder_test/
├── actions/                          # Action层 - 业务动作封装
│   ├── base/                         # 基础Action
│   │   ├── base_action.py           # BaseAction基类
│   │   ├── action_result.py         # ActionResult结果类
│   │   └── action_context.py        # ActionContext上下文类
│   ├── motor_action.py              # ASDB2电机动作（新增）
│   ├── motor/                        # 电机动作
│   ├── encoder/                      # 编码器动作
│   ├── power/                        # 电源动作
│   └── common/                       # 通用动作
│
├── core/                             # 核心层
│   ├── checks/                       # Check层 - 断言层（新增）
│   │   ├── __init__.py
│   │   └── speed_check.py           # 速度断言
│   ├── collectors/                   # Collector层 - 数据采集层（新增）
│   │   ├── __init__.py
│   │   └── speed_collector.py       # 速度数据采集
│   └── testcase/                     # TestCase层 - 测试业务逻辑层
│       ├── base/                     # 基础TestCase
│       │   ├── base_case.py         # BaseCase基类
│       │   ├── case_result.py       # CaseResult结果类
│       │   └── case_context.py      # CaseContext上下文类
│       └── asdb2/                    # ASDB2测试用例（新增）
│           ├── __init__.py
│           └── asdb2_speed_control_case.py
│
├── data/                             # Data层 - 测试数据层（新增）
│   └── speed.yaml                    # 速度测试数据
│
├── tests/                            # Pytest TestCase层 - 测试用例执行层
│   └── asdb2/                        # ASDB2测试（新增）
│       ├── __init__.py
│       └── test_speed_control.py    # 速度控制测试
│
├── drivers/                          # Driver层 - 设备驱动层
│   └── device/
│       └── ASDB2/
│           ├── asdb2_driver.py       # ASDB2驱动器
│           └── tests/                # 驱动层测试（旧版）
│
└── conftest.py                       # Pytest配置文件（已更新）
```

## 各层职责

### 1. Driver层（设备驱动层）

**职责：**
- 只负责设备控制
- 提供基础的设备操作接口
- 不写测试逻辑

**示例：**
```python
class ASDB2Driver(BaseDevice):
    def connect() -> bool
    def disconnect()
    def enable_servo(enable: bool) -> bool
    def disable_servo() -> bool
    def set_speed(p1_09, p1_10, p1_11) -> bool
    def read_feedback_speed() -> float
    def run_motor(speed_rpm, direction, source) -> bool
    def stop_motor() -> bool
```

### 2. Action层（业务动作封装层）

**职责：**
- 封装业务动作
- 隐藏底层寄存器和协议细节
- 提供业务级别的动作接口

**示例：**
```python
class MotorAction(BaseAction):
    def enable_servo(enable: bool) -> ActionResult
    def run_speed(rpm, direction, source) -> ActionResult
    def stop() -> ActionResult
    def read_speed() -> ActionResult
    def set_speed(p1_09, p1_10, p1_11) -> ActionResult
    def initialize() -> ActionResult
```

**使用示例：**
```python
motor = MotorAction(driver)
motor.run_speed(1000, direction='CW', source='P1-11')
motor.stop()
motor.enable_servo()
```

### 3. Collector层（数据采集层）

**职责：**
- 采集测试数据
- 支持连续采样
- 返回结构化数据

**示例：**
```python
class SpeedCollector:
    def collect(duration, interval) -> List[Tuple[float, float]]
    def collect_single() -> Optional[float]
    def get_statistics(data) -> dict
```

**使用示例：**
```python
collector = SpeedCollector(motor)
data = collector.collect(duration=10, interval=0.1)
# data = [(time, speed), (time, speed), ...]
```

### 4. Check层（断言层）

**职责：**
- 提供断言方法
- 支持容忍度配置
- 提供清晰的断言消息

**示例：**
```python
class SpeedCheck:
    @staticmethod
    def stable(actual, target, tolerance) -> bool
    @staticmethod
    def in_range(speed, min_speed, max_speed) -> bool
    @staticmethod
    def zero(speed, tolerance) -> bool
    @staticmethod
    def direction_match(speed, direction) -> bool
```

**使用示例：**
```python
SpeedCheck.stable(actual=998, target=1000, tolerance=5)
SpeedCheck.in_range(speed=500, min_speed=0, max_speed=3000)
```

### 5. TestCase层（测试业务逻辑层）

**职责：**
- 真正的测试逻辑
- 使用Action、Collector、Check
- 不直接操作寄存器
- 不关心通讯协议

**示例：**
```python
class ASDB2SpeedControlCase(BaseCase):
    def setup():
        self.motor = motor
        self.collector = SpeedCollector(self.motor)
    
    def run():
        # 1. 初始化
        self.motor.initialize()
        
        # 2. 使能伺服
        self.motor.enable_servo(True)
        
        # 3. 运行电机
        self.motor.run_speed(1000, 'CW', 'P1-11')
        
        # 4. 读取速度
        result = self.motor.read_speed()
        speed = result.data.get('feedback_speed')
        
        # 5. 检查速度
        SpeedCheck.stable(speed, 1000, 10)
        
        # 6. 采集数据
        data = self.collector.collect(duration=5, interval=0.1)
        
        # 7. 停止电机
        self.motor.stop()
```

### 6. Pytest TestCase层（测试用例执行层）

**职责：**
- 使用pytest框架执行测试
- 使用fixture管理资源
- 使用参数化测试
- 支持数据驱动测试

**示例：**
```python
@pytest.fixture(scope="session")
def asdb2_driver():
    driver = ASDB2Driver(...)
    driver.connect()
    yield driver
    driver.disconnect()

@pytest.fixture
def motor(asdb2_driver):
    motor = MotorAction(asdb2_driver)
    yield motor
    motor.stop()

@pytest.mark.parametrize("case_data", load_speed_cases())
def test_speed_control(motor, case_data):
    case = ASDB2SpeedControlCase(motor=motor, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

### 7. Data层（测试数据层）

**职责：**
- 分离测试数据
- 使用YAML格式
- 方便测试人员维护

**示例：**
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

## 使用流程

### 1. 运行所有测试

```bash
cd backend/projects/encoder_test
pytest tests/asdb2/test_speed_control.py -v
```

### 2. 运行单个测试

```bash
pytest tests/asdb2/test_speed_control.py::TestASDB2SpeedControl::test_speed_control -v
```

### 3. 运行参数化测试

```bash
pytest tests/asdb2/test_speed_control.py::TestASDB2SpeedControl::test_speed_control -v
```

### 4. 运行特定速度源的测试

```bash
pytest tests/asdb2/test_speed_control.py -k "p1_09" -v
```

### 5. 查看测试报告

```bash
pytest tests/asdb2/test_speed_control.py -v --html=report.html
```

## 架构优势

### 1. 分层清晰
- 每层职责明确
- 不跨层调用
- 易于维护和扩展

### 2. 解耦彻底
- Driver不写测试逻辑
- Action不关心寄存器
- TestCase不关心协议

### 3. 复用性强
- Action可复用
- Check可复用
- Collector可复用

### 4. 可扩展性强
- 添加新设备只需添加Driver
- 添加新动作只需添加Action
- 添加新测试只需添加TestCase

### 5. 数据驱动
- 测试数据与代码分离
- 方便测试人员维护
- 支持参数化测试

### 6. 工业级稳定性
- 支持回滚机制
- 支持错误恢复
- 支持日志记录

## 对比旧版架构

### 旧版架构（不推荐）

```python
def test_speed_control():
    driver = ASDB2Driver()
    driver.connect()
    driver.initialize_driver()
    driver.set_speed(p1_09=10, p1_10=100, p1_11=1000)
    driver.enable_servo(True)
    driver.run_motor(speed_rpm=10, direction='CW', source='P1-09')
    time.sleep(5)
    feedback_speed = driver.read_feedback_speed()
    assert abs(feedback_speed - 10) <= 2
    driver.stop_motor()
    driver.enable_servo(False)
    driver.disconnect()
```

**问题：**
- 直接操作寄存器
- 直接调用协议
- 测试逻辑与设备控制耦合
- 难以复用
- 难以维护

### 新版架构（推荐）

```python
@pytest.mark.parametrize("case_data", load_speed_cases())
def test_speed_control(motor, case_data):
    case = ASDB2SpeedControlCase(motor=motor, case_data=case_data)
    result = case.execute()
    assert result.status.value == 'passed'
```

**优势：**
- 不直接操作寄存器
- 不关心通讯协议
- 测试逻辑清晰
- 易于复用
- 易于维护
- 支持参数化测试
- 支持数据驱动

## 未来扩展

### 1. 接入TestEngine
- TestCase已经标准化
- 可以直接接入TestEngine
- 支持远程执行
- 支持任务调度

### 2. 接入数字孪生
- Driver层可以接入数字孪生
- Action层无需修改
- TestCase层无需修改

### 3. 接入测试平台
- Pytest TestCase可以接入测试平台
- 支持Web界面
- 支持报告生成
- 支持数据分析

### 4. 添加更多设备
- 添加新的Driver
- 添加新的Action
- 添加新的Check
- 添加新的Collector
- 添加新的TestCase

### 5. 添加更多测试
- 添加速度稳定性测试
- 添加加速度测试
- 添加位置精度测试
- 添加长时间运行测试
- 添加压力测试

## 总结

这个架构完全符合工业测试平台的要求：

1. **分层清晰**：Driver -> Action -> Collector -> Check -> TestCase -> Pytest
2. **解耦彻底**：每层职责明确，不跨层调用
3. **复用性强**：Action、Check、Collector都可以复用
4. **可扩展性强**：添加新功能只需添加对应层的代码
5. **数据驱动**：测试数据与代码分离
6. **工业级稳定性**：支持回滚、错误恢复、日志记录

这个架构可以支撑上百上千条自动化用例，而且可以轻松接入TestEngine、数字孪生、测试平台等系统。