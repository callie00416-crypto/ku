工业自动化测试平台架构规则（最终冻结版）
版本：V5.0-Lite
状态：永久冻结
适用范围：backend 全域
数据库：MySQL 8.x
架构等级：工业平台第一代长期稳定架构

---
一、平台终极定位（永久不变）
本系统不是单项目系统。
本系统是：
工业自动化测试平台（Industrial Automation Platform）
用于承载：
- 编码器测试
- AOI检测
- ATS测试
- 工业老化测试
- 工装测试
- 单产线MES
- 自动化测试平台
因此：
平台层（Platform）
与
项目层（Projects）
必须永久隔离。

---
二、最终目录结构（永久冻结）
backend/
├── platform/                    # ⭐ 工业平台内核（永久稳定）
│   ├── runtime/                # Runtime、EventBus、Actor、Snapshot
│   ├── domain/                 # DDD 领域模型（通用抽象）
│   │   ├── common/            # AggregateRoot、StateMachine
│   │   ├── device/            # 通用设备抽象
│   │   ├── task/              # 通用任务抽象
│   │   ├── station/           # 通用工位抽象
│   │   ├── alarm/             # 通用告警抽象
│   │   └── report/            # 通用报告抽象
│   ├── storage/                # CQRS 存储、Repository
│   ├── application/            # 通用应用服务
│   └── api/                    # 平台 API
│
├── projects/                   # ⭐ 所有工业项目
│   └── encoder_test/          # 编码器测试项目
│       ├── actions/           # 编码器/电机/电源动作
│       ├── drivers/           # 编码器/电机/电源驱动
│       ├── testcases/         # 编码器测试用例
│       ├── flows/             # 编码器测试流程
│       ├── configs/           # 编码器测试配置
│       └── adapters/          # ⭐ 平台适配层
│           ├── device_adapter.py      # EncoderDevice → Platform Device
│           ├── task_adapter.py        # EncoderTestCase → Platform Task
│           └── station_adapter.py     # EncoderStation → Platform Station
│
├── shared/                     # ⭐ 通用工具
│   ├── drivers/               # 可复用的驱动
│   │   ├── base/             # BaseComm、BaseProtocol、BaseDevice
│   │   ├── comm/             # RS485、TCP、CAN
│   │   └── protocol/         # Modbus、SCPI
│   ├── utils/                 # 工具函数
│   └── logging/               # 日志系统
│
├── conf/                       # Django 配置
└── manage.py

---
三、平台层 vs 项目层（永久边界）
1. platform = 工业平台内核
platform 是：
工业Runtime平台。
平台层必须：
- 通用
- 稳定
- 长期不变
- 不包含项目业务
禁止：
- 编码器业务
- AOI业务
- 特定设备逻辑
- 特定工艺逻辑

---
2. projects = 项目业务实现
projects 是：
具体工业项目。
允许：
- 编码器逻辑
- 电机流程
- AOI算法
- 特定工艺
禁止：
- 修改平台内核
- 修改DDD核心规则
- 修改Runtime机制

---
四、Shared层定位（永久冻结）
shared 是：
可跨项目复用能力。
包括：
- BaseComm
- BaseProtocol
- TCP/RS485/CAN
- Modbus/SCPI
- 通用日志
- 通用工具
shared 不是：
业务层。
禁止：
- 工单逻辑
- 测试逻辑
- Runtime逻辑

---
五、Runtime层规则（工业铁律）
目录：
platform/runtime/
Runtime只允许：
- Actor
- EventBus
- Mailbox
- Snapshot
- Recovery
- Tick
- Backpressure
- HealthMonitor
禁止：
- ORM
- MySQL
- Django Model
- 工艺规则
- 工单逻辑
Runtime必须：
- 零阻塞
- 零IO
- 零数据库操作

---
六、DDD领域规则（永久冻结）
目录：
platform/domain/
Domain必须：
- 纯Python
- 无框架依赖
- 无数据库依赖
- 无ORM
禁止：
import django
import sqlalchemy
import pymysql

---
七、Application层规则
目录：
platform/application/
允许：
- 流程编排
- Handler
- Repository调用
- 事务协调
- 调用Domain
- 调用Repository Interface
禁止：
- 业务规则
- 状态机
- 工艺if-else
- 超长Service
Application层禁止膨胀。

---
八、Storage层规则
目录：
platform/storage/
允许：
- SQLAlchemy
- MySQL
- CRUD
- Query
禁止：
- Runtime逻辑
- 工艺逻辑
- 状态机
- 业务规则

---
九、数据库规则（MySQL冻结版）
数据库：
MySQL 8.x
字符集：
utf8mb4
排序规则：
utf8mb4_unicode_ci
主数据库：
MySQL 8.0+
存储引擎：
InnoDB（强制）
字符集：
utf8mb4
排序规则：
utf8mb4_unicode_ci
========================================================
15.1 MySQL 工业选型原则
本平台选择 MySQL 而非 PostgreSQL 的核心原因：
工业现场部署更简单
Windows/Linux兼容成熟
运维人员普及率更高
中小工业项目维护成本更低
单机/小集群稳定性成熟
工控机环境兼容性更强
本平台当前不是：
互联网超大规模分布式系统。
因此：
不追求 PostgreSQL 高级特性。
优先：
稳定性、可维护性、工业现场可部署性。
========================================================
15.2 永久数据库铁律
禁止：
CASCADE DELETE
复杂触发器
存储过程业务逻辑
数据库业务规则
跨库事务
重型分布式数据库
统一：
PROTECT / RESTRICT
所有业务规则：
必须回归 Domain 层。
========================================================
15.3 所有表强制字段
所有核心表必须包含：
id
version
created_at
updated_at
工业时间维度：
occurred_at
persisted_at
processed_at
========================================================
15.4 乐观锁永久规则
所有聚合根：
必须使用：
version 乐观锁。
禁止：
悲观锁大面积滥用。
========================================================
15.5 JSON字段规则
允许：
JSON字段。
仅用于：
设备配置
扩展参数
非核心结构化数据
禁止：
核心业务结构完全JSON化。
核心业务数据：
必须结构化建模。
========================================================
15.6 索引规则
必须建立：
task_id
workorder_id
station_id
device_id
created_at
status
相关索引。
禁止：
无索引全表扫描。
========================================================
15.7 工业长期稳定规则
数据库设计目标：
可追溯
可恢复
可审计
可长期维护
而不是：
极限性能炫技
超复杂SQL优化
理论化数据库设计
========================================================
15.8 ORM规则
允许：
Django ORM
SQLAlchemy
但：
ORM 仅属于 Storage 层。
禁止：
ORM 泄漏到：
Runtime
Domain
Application
========================================================
15.9 未来扩展规则（暂不实现）
未来允许扩展：
ClickHouse
InfluxDB
TimescaleDB
用于：
时序波形、大规模指标分析。
当前阶段：
禁止提前建设。


---
十、工业数据时间语义（永久冻结）
所有核心表必须包含：
created_at
业务创建时间
occurred_at
现场真实发生时间
persisted_at
数据库落地时间
processed_at
系统处理完成时间
禁止混用。


---
十一、工业事件体系（永久冻结）
只允许两类事件：
RuntimeEvent
描述：
- 设备断连
- 心跳丢失
- TCP异常
- PLC异常
- 队列溢出
禁止：
- 工单完成
- 测试通过
- 工艺推进

---
DomainEvent
描述：
- 任务完成
- 测试完成
- 工单流转
- 报告归档

---
十二、Actor邮箱治理（工业强约束）
所有Actor必须：
- 固定容量
- 禁止无限队列

---
消息等级
CRITICAL
禁止丢弃：
- 急停
- 安全联锁
- 测试最终结果
- 严重告警

---
NORMAL
允许：
DROP_OLD

---
TRANSIENT
允许：
覆盖旧状态

---
十三、Snapshot规则（永久冻结）
只允许快照：
- Actor状态
- 运行中任务
- 设备连接态
- 未完成流程
禁止：
- 历史数据
- 已完成任务
- 全量队列
- 临时缓存

---
十四、Recovery恢复规则
系统恢复后：
禁止直接信赖Snapshot。
必须：
- Domain重新校验状态
- 重新检查设备在线状态
- 重新校验工艺一致性
- 所有恢复流程必须幂等

---
十五、Adapter层规则（极其重要）
目录：
projects/*/adapters/
Adapter是：
项目业务
→
平台通用领域
之间的转换层。
例如：
EncoderDevice
→
Platform Device
EncoderTask
→
Platform Task

---
Adapter允许：
- DTO转换
- 参数映射
- 配置转换

---
Adapter禁止：
- 业务规则
- Runtime控制
- Repository操作

---
十六、AI生成代码强规则
AI生成代码时：
必须：
- 遵守Platform/Project分层
- 遵守DDD
- 遵守Runtime隔离
- 遵守MySQL规范
- 优先简单方案
- 优先稳定方案
- 优先低复杂度
- 优先工业可维护性
禁止：
- 项目层直接操作Platform Runtime
- Domain import ORM
- Runtime操作数据库
- Application写业务逻辑
- 巨型Service
- 超前抽象
- 自动重构目录
- 引入新架构层
- 引入微服务
- 引入Kafka
- 引入复杂DSL
- 引入Saga
- 引入事件溯源
- 引入复杂依赖注入框架
- 修改冻结分层

---
十七、当前允许技术栈（永久冻结）
允许：
- Python 3.11+
- Django
- SQLAlchemy
- MySQL
- Redis
- asyncio
禁止新增：
- 微服务
- Kafka
- EventSourcing
- WAL
- Kubernetes复杂编排
- Workflow DSL
- Saga
========================================================
工业第一原则（最高规则）
========================================================

任何设计决策：

优先级判断：

工业稳定性
    >
可排障性
    >
可恢复性
    >
可维护性
    >
性能
    >
架构优雅
    >
理论先进性

---
十八、当前唯一开发重点（永久路线）
后续只允许重点投入：
1. 真实设备联调
包括：
- PLC
- TCP
- 串口
- Modbus
- 工业相机

---
2. 工业异常恢复
包括：
- 断电恢复
- Snapshot恢复
- 自动重连
- 幂等恢复

---
3. 坏现场稳定性
包括：
- 网络抖动
- PLC假死
- MySQL抖动
- Redis断连
- Actor雪崩

---
十九、终极冻结结论
平台架构已最终定型。
永久停止：
- 架构重构
- 大规模目录调整
- 理论升级
- 超前抽象
全面进入：
工业稳定性打磨阶段。
最终目标：
构建可稳定运行5年以上的工业级Runtime平台。

