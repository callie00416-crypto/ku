-- 工业自动化测试平台数据库Schema
-- PostgreSQL Schema 固化
-- 包含：全表、全索引、全约束、全唯一键、全时间字段、全version字段

-- 1. work_order table (工业业务主链路)
CREATE TABLE IF NOT EXISTS work_orders (
    id SERIAL PRIMARY KEY,
    workorder_id VARCHAR(64) UNIQUE NOT NULL,
    product_model VARCHAR(128) NOT NULL,
    batch_number VARCHAR(64),
    planned_quantity INTEGER DEFAULT 0,
    completed_quantity INTEGER DEFAULT 0,
    ng_quantity INTEGER DEFAULT 0,
    route_config JSONB,  -- 工艺路线配置
    priority INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'PENDING',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 2. task table (工业核心)
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(64) UNIQUE NOT NULL,
    workorder_id VARCHAR(64),
    station_id INTEGER,
    device_id VARCHAR(64),
    sn VARCHAR(128),  -- 产品序列号
    task_type VARCHAR(64),
    priority INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'PENDING',
    result VARCHAR(32),
    error_code VARCHAR(64),
    error_message TEXT,
    max_retries INTEGER DEFAULT 3,
    retry_count INTEGER DEFAULT 0,
    actor_id VARCHAR(64),  -- 执行者ID
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms BIGINT,  -- 任务执行时长(毫秒)
    metrics JSONB,  -- 任务指标
    trace_id VARCHAR(64),  -- 追踪ID
    correlation_id VARCHAR(64),  -- 关联ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 3. station table (工位信息)
CREATE TABLE IF NOT EXISTS stations (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    location VARCHAR(128),
    status VARCHAR(32) DEFAULT 'IDLE',
    config JSONB,  -- 工位配置
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 4. device table (设备信息)
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    device_type VARCHAR(64),
    station_id INTEGER,
    ip_address VARCHAR(64),
    port INTEGER,
    status VARCHAR(32) DEFAULT 'OFFLINE',
    connection_info JSONB,  -- 连接信息
    config JSONB,  -- 设备配置
    health_status JSONB,  -- 健康状态
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 5. alarm table (告警信息)
CREATE TABLE IF NOT EXISTS alarms (
    id SERIAL PRIMARY KEY,
    alarm_id VARCHAR(64) UNIQUE NOT NULL,
    station_id INTEGER,
    device_id VARCHAR(64),
    alarm_type VARCHAR(64),
    severity VARCHAR(16) DEFAULT 'WARNING',  -- INFO, WARNING, ERROR, CRITICAL
    title VARCHAR(256),
    description TEXT,
    status VARCHAR(32) DEFAULT 'ACTIVE',
    dedup_key VARCHAR(128),  -- 告警去重Key
    resolved_by VARCHAR(64),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 6. report table (测试报告 - 最关键工业追溯)
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(64) UNIQUE NOT NULL,
    task_id VARCHAR(64),
    workorder_id VARCHAR(64),
    sn VARCHAR(128),  -- 产品序列号
    station_id INTEGER,
    device_id VARCHAR(64),
    result VARCHAR(32),
    detail JSONB,  -- 详细测试结果
    report_snapshot JSONB,  -- 报告快照（5年追溯用）
    -- 快照内容包括：
    -- task snapshot
    -- device snapshot
    -- station snapshot
    -- config snapshot
    -- alarm snapshot
    attachments JSONB,  -- 附件系统（波形、图片、CSV、原始日志、PLC数据等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 7. test_record table (测试记录)
CREATE TABLE IF NOT EXISTS test_records (
    id SERIAL PRIMARY KEY,
    record_id VARCHAR(64) UNIQUE NOT NULL,
    task_id VARCHAR(64),
    report_id VARCHAR(64),
    test_item VARCHAR(128),  -- 测试项
    expected_value VARCHAR(256),
    actual_value VARCHAR(256),
    tolerance VARCHAR(64),  -- 公差
    result VARCHAR(32),  -- PASS/FAIL
    unit VARCHAR(32),  -- 单位
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 8. event_log table (事件日志 - 用于追溯和审计)
CREATE TABLE IF NOT EXISTS event_logs (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(64) UNIQUE NOT NULL,
    event_type VARCHAR(64),
    source_type VARCHAR(64),  -- TASK, STATION, DEVICE, ALARM, REPORT
    source_id VARCHAR(64),  -- 源ID
    payload JSONB,  -- 事件载荷
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 现场真实发生时间
    persisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 数据库落地时间
    processed_at TIMESTAMP,  -- 业务处理时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 9. user table (用户 - RBAC轻量版)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email VARCHAR(128),
    role VARCHAR(32) DEFAULT 'OPERATOR',  -- ADMIN, ENGINEER, OPERATOR
    status VARCHAR(32) DEFAULT 'ACTIVE',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 10. system_config table (系统配置)
CREATE TABLE IF NOT EXISTS system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(128) UNIQUE NOT NULL,
    config_value JSONB,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 创建索引以提高查询性能

-- task table indexes
CREATE INDEX IF NOT EXISTS idx_task_sn ON tasks(sn);
CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_task_station ON tasks(station_id);
CREATE INDEX IF NOT EXISTS idx_task_created ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_task_workorder ON tasks(workorder_id);
CREATE INDEX IF NOT EXISTS idx_task_trace_id ON tasks(trace_id);
CREATE INDEX IF NOT EXISTS idx_task_correlation_id ON tasks(correlation_id);
CREATE INDEX IF NOT EXISTS idx_task_started_completed ON tasks(started_at, completed_at);

-- report table indexes
CREATE INDEX IF NOT EXISTS idx_report_sn ON reports(sn);
CREATE INDEX IF NOT EXISTS idx_report_workorder ON reports(workorder_id);
CREATE INDEX IF NOT EXISTS idx_report_task ON reports(task_id);
CREATE INDEX IF NOT EXISTS idx_report_station ON reports(station_id);
CREATE INDEX IF NOT EXISTS idx_report_result ON reports(result);
CREATE INDEX IF NOT EXISTS idx_report_created ON reports(created_at);

-- alarm table indexes
CREATE INDEX IF NOT EXISTS idx_alarm_station ON alarms(station_id);
CREATE INDEX IF NOT EXISTS idx_alarm_device ON alarms(device_id);
CREATE INDEX IF NOT EXISTS idx_alarm_type ON alarms(alarm_type);
CREATE INDEX IF NOT EXISTS idx_alarm_status ON alarms(status);
CREATE INDEX IF NOT EXISTS idx_alarm_dedup_key ON alarms(dedup_key);
CREATE INDEX IF NOT EXISTS idx_alarm_created ON alarms(created_at);

-- work_order table indexes
CREATE INDEX IF NOT EXISTS idx_workorder_product ON work_orders(product_model);
CREATE INDEX IF NOT EXISTS idx_workorder_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_workorder_start_end ON work_orders(start_time, end_time);

-- station table indexes
CREATE INDEX IF NOT EXISTS idx_station_status ON stations(status);
CREATE INDEX IF NOT EXISTS idx_station_location ON stations(location);

-- device table indexes
CREATE INDEX IF NOT EXISTS idx_device_type ON devices(device_type);
CREATE INDEX IF NOT EXISTS idx_device_station ON devices(station_id);
CREATE INDEX IF NOT EXISTS idx_device_status ON devices(status);

-- test_record table indexes
CREATE INDEX IF NOT EXISTS idx_test_record_task ON test_records(task_id);
CREATE INDEX IF NOT EXISTS idx_test_record_report ON test_records(report_id);
CREATE INDEX IF NOT EXISTS idx_test_record_item ON test_records(test_item);
CREATE INDEX IF NOT EXISTS idx_test_record_result ON test_records(result);

-- event_log table indexes
CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_event_log_source ON event_logs(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_event_log_occurred ON event_logs(occurred_at);
CREATE INDEX IF NOT EXISTS idx_event_log_persisted ON event_logs(persisted_at);