# encoder_test 项目导入规范

## 问题背景

`encoder_test` 不再标记为源代码根目录，唯一的源代码根目录是 `backend`。

## 导入规则

### 1. 绝对导入规则（强制）

所有导入必须从 `backend` 源代码根目录开始，使用绝对导入。

#### ❌ 错误的导入方式
```python
# 假设 encoder_test 是源代码根目录的导入
from core.testcase.base.base_case import BaseCase
from actions import DelayAction
from actions.base import BaseAction
from core.testcase.encoder.encoder_power_cycle_case import EncoderPowerCycleCase
```

#### ✅ 正确的导入方式
```python
# 从 backend 源代码根目录开始的绝对导入
from projects.encoder_test.core.testcase.base.base_case import BaseCase
from projects.encoder_test.actions import DelayAction
from projects.encoder_test.actions.base import BaseAction
from projects.encoder_test.core.testcase.encoder.encoder_power_cycle_case import EncoderPowerCycleCase
```

### 2. 同项目内导入规则

在 `encoder_test` 项目内部，所有导入都必须包含 `projects.encoder_test` 前缀。

#### 示例
```python
# 在 projects/encoder_test/core/testcase/encoder/encoder_power_cycle_case.py 中
from projects.encoder_test.core.testcase.base.base_case import BaseCase
from projects.encoder_test.actions import DelayAction

# 在 projects/encoder_test/actions/encoder/encoder_action.py 中
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.drivers.device.encoder.dpt_encoder_factory import DPTEncoder
```

### 3. 跨项目导入规则

当需要导入其他项目或共享模块时，也必须从 `backend` 根目录开始。

#### 示例
```python
# 导入共享模块
from shared.drivers.base.base_device import BaseDevice
from shared.drivers.comm.serial_comm import SerialComm
from shared.drivers.protocol.scpi_protocol import SCPIProtocol

# 导入其他项目（如果有）
from projects.other_project.some_module import SomeClass
```

### 4. 相对导入规则

在同一个包内部，允许使用相对导入，但建议优先使用绝对导入。

#### 示例
```python
# 在 projects/encoder_test/core/testcase/encoder/ 目录下
# 允许的相对导入
from .base_case import BaseCase
from ..base.case_result import CaseResult

# 推荐的绝对导入
from projects.encoder_test.core.testcase.base.base_case import BaseCase
from projects.encoder_test.core.testcase.base.case_result import CaseResult
```

### 5. __init__.py 导出规则

在 `__init__.py` 文件中，导出时也必须使用绝对导入。

#### 示例
```python
# projects/encoder_test/actions/__init__.py
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.flow.base_flow import BaseFlow
from projects.encoder_test.actions.common.common_action import DelayAction

__all__ = [
    'BaseAction',
    'BaseFlow',
    'DelayAction',
]
```

## 迁移指南

### 需要修改的文件类型

1. **所有 Python 源文件** (.py)
2. **所有 __init__.py 文件**
3. **测试文件**

### 自动化替换规则

使用以下正则表达式进行批量替换：

#### 替换规则 1：core 模块导入
```regex
# 查找
^from core\.

# 替换为
from projects.encoder_test.core.
```

#### 替换规则 2：actions 模块导入
```regex
# 查找
^from actions\.

# 替换为
from projects.encoder_test.actions.
```

#### 替换规则 3：drivers 模块导入
```regex
# 查找
^from drivers\.

# 替换为
from projects.encoder_test.drivers.
```

#### 替换规则 4：configs 模块导入
```regex
# 查找
^from configs\.

# 替换为
from projects.encoder_test.configs.
```

### 手动检查清单

- [ ] 所有 `from core.` 导出已替换为 `from projects.encoder_test.core.`
- [ ] 所有 `from actions.` 导出已替换为 `from projects.encoder_test.actions.`
- [ ] 所有 `from drivers.` 导出已替换为 `from projects.encoder_test.drivers.`
- [ ] 所有 `from configs.` 导出已替换为 `from projects.encoder_test.configs.`
- [ ] 所有 `__init__.py` 文件已更新
- [ ] 所有测试文件已更新
- [ ] 运行测试确保没有导入错误

## 常见问题

### Q1: 为什么不能使用相对导入？

A: 虽然相对导入在语法上是允许的，但在工业平台中，绝对导入具有以下优势：
- 更清晰的依赖关系
- 更容易重构和移动代码
- 避免循环导入问题
- 更好的 IDE 支持和代码导航

### Q2: 如果导入路径太长怎么办？

A: 可以考虑以下方案：
1. 在 `__init__.py` 中重新导出常用类
2. 使用别名简化导入
3. 评估模块结构是否合理

### Q3: 如何处理循环导入？

A: 循环导入通常表示设计问题，解决方案：
1. 重构代码，消除循环依赖
2. 使用延迟导入（在函数内部导入）
3. 引入中间层来解耦

### Q4: 测试文件如何导入？

A: 测试文件也应该遵循相同的导入规则：

```python
# tests/test_encoder_power_cycle.py
from projects.encoder_test.core.testcase.encoder.encoder_power_cycle_case import (
    EncoderPowerCycleCase,
    EncoderPowerCycleTestRunner
)
from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier
```

## 工具支持

### PyCharm 配置

1. **标记源代码根目录**
   - 只标记 `backend` 为源代码根目录
   - 不要标记 `projects/encoder_test` 为源代码根目录

2. **代码检查**
   - 启用导入检查
   - 设置为拒绝相对导入（可选）

3. **代码格式化**
   - 配置自动排序导入
   - 确保导入语句符合规范

### VS Code 配置

1. **Python 分析配置**
   ```json
   {
     "python.analysis.extraPaths": [
       "${workspaceFolder}/backend"
     ],
     "python.linting.pylintArgs": [
       "--init-hook",
       "import sys; sys.path.insert(0, '${workspaceFolder}/backend')"
     ]
   }
   ```

## 示例文件

### 正确的导入示例

```python
"""
编码器上断电测试用例
"""
from typing import Any, Dict, List
from projects.encoder_test.core.testcase.base.base_case import BaseCase
from projects.encoder_test.actions import DelayAction
import logging
import time

logger = logging.getLogger(__name__)


class EncoderPowerCycleCase(BaseCase):
    """编码器上断电循环测试用例"""
    
    def __init__(
        self,
        power_amplifier: Any = None,
        waveform_generator: Any = None,
        encoder: Any = None,
        case_id: str = "encoder_power_cycle",
        description: str = "编码器上断电循环测试",
        use_mock: bool = False,
        **kwargs
    ):
        super().__init__(case_id=case_id, description=description, **kwargs)
        self._power_amplifier = power_amplifier
        self._waveform_generator = waveform_generator
        self._encoder = encoder
        self._use_mock = use_mock
        self._cycle_results: List[Dict] = []
    
    def setup(self):
        """设置测试用例"""
        if self._use_mock:
            self.log("使用Mock设备进行测试")
            if self._power_amplifier is None:
                from projects.encoder_test.core.testcase.encoder.encoder_power_cycle_case import MockPowerAmplifier
                self._power_amplifier = MockPowerAmplifier()
            if self._waveform_generator is None:
                from projects.encoder_test.core.testcase.encoder.encoder_power_cycle_case import MockWaveformGenerator
                self._waveform_generator = MockWaveformGenerator()
            if self._encoder is None:
                from projects.encoder_test.core.testcase.encoder.encoder_power_cycle_case import MockEncoder
                self._encoder = MockEncoder()
        
        if self._power_amplifier:
            self.set_device('power_amplifier', self._power_amplifier)
        if self._waveform_generator:
            self.set_device('waveform_generator', self._waveform_generator)
        if self._encoder:
            self.set_device('encoder', self._encoder)
```

## 强制执行

### Lint 规则

建议在项目中配置 lint 规则来强制执行导入规范：

```python
# setup.cfg 或 pyproject.toml
[pylint.messages_control]
disable=[
    "C0103",  # 允许短变量名
]
enable=[
    "W0403",  # 禁止相对导入
]

[pylint.IMPORTS]
deprecated-modules=
    "core",  # 禁止直接导入 core
    "actions",  # 禁止直接导入 actions
```

### Pre-commit Hook

配置 pre-commit hook 来检查导入规范：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-imports
        name: Check imports
        entry: python scripts/check_imports.py
        language: system
        files: ^projects/encoder_test/.*\.py$
```

## 总结

1. **唯一源代码根目录**: `backend`
2. **强制绝对导入**: 所有导入必须从 `backend` 开始
3. **项目前缀**: encoder_test 项目内导入必须包含 `projects.encoder_test` 前缀
4. **共享模块**: 使用 `shared` 前缀导入共享模块
5. **工具支持**: 配置 IDE 和 lint 工具来强制执行规范

遵循这些规则可以确保代码的一致性和可维护性。