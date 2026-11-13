---
alwaysApply: true
---
# 1. 模块导入禁止副作用
- 禁止在模块顶层（import 时）执行：实例化、IO操作、线程创建、异步启动、连接初始化
- 所有全局单例必须改为：延迟获取函数（get_xxx()），禁止直接全局实例化
导入行为
禁止 import 副作用
禁止 import 时启动系统
禁止 import 时创建线程
禁止 import 时初始化连接
导入语法
禁止 from xxx import *
跨 package 必须绝对导入
同 package 允许一级相对导入
禁止跨层级相对导入
架构约束
禁止循环依赖
依赖必须单向
domain 禁止依赖 infra
import 必须可静态分析
全局对象
禁止全局直接实例化
必须使用 get_xxx()
推荐统一 Container 管理

# 2. 应用就绪方法（ready()）极简原则
- ready() 仅允许：对象构造（纯内存操作，无IO/无阻塞）
- 禁止在 ready() 中：enable_async()、addHandler()、文件操作、网络请求、线程启动
- 禁止在 ready() 中执行任何 Initialize/Start 逻辑

# 3. 三阶段生命周期强制分离（工业标准）
- Construct（构造）：仅创建空对象，无依赖、无IO、无阻塞 → 允许在 ready()/get_xxx() 中
- Initialize（初始化）：配置赋值、依赖注入 → 禁止在 ready() 中
- Start（启动）：IO、异步、线程、处理器、连接 → 必须由外部显式调用

# 4. 单例模式统一规范
- 全局单例统一使用：延迟初始化函数（get_event_bus()/get_logger_manager()）
- 函数内懒加载实例，禁止模块顶层预创建实例
- 禁止单例构造时自动执行启动逻辑

# 5. 异步/日志/IO 操作强制规则
- 异步启动、日志处理器、文件写入：必须显式调用，禁止自动执行
- 禁止在导入、构造、ready() 阶段触发任何阻塞操作

【强制规则】
反模式标记：
global instance at module top
ready() enable_async
auto start on construct
import time IO

合规模式标记：
lazy init get_xxx()
three-stage lifecycle
explicit start
ready() only construct

请按以上规则生成/审查代码。