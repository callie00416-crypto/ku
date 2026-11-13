"""
Initial migration for Industrial Automation Test Platform
Creates all tables for the industrial automation system
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to this revision - creates all tables"""
    
    # 1. work_order table (工业业务主链路)
    op.create_table('work_orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('workorder_id', sa.String(length=64), nullable=False),
        sa.Column('product_model', sa.String(length=128), nullable=False),
        sa.Column('batch_number', sa.String(length=64), nullable=True),
        sa.Column('planned_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('completed_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('ng_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('route_config', sa.JSON(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, default=0, index=True),
        sa.Column('status', sa.String(length=32), nullable=False, default='PENDING', index=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workorder_id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_work_orders_batch_number'), 'work_orders', ['batch_number'], unique=False)
    
    # 2. task table (工业核心)
    op.create_table('tasks',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('workorder_id', sa.String(length=64), nullable=True),
        sa.Column('station_id', sa.Integer(), nullable=True),
        sa.Column('device_id', sa.String(length=64), nullable=True),
        sa.Column('sn', sa.String(length=128), nullable=True),
        sa.Column('task_type', sa.String(length=32), nullable=False),
        sa.Column('priority', sa.String(length=16), nullable=False, default='normal'),
        sa.Column('status', sa.String(length=32), nullable=False, default='pending'),
        sa.Column('result', sa.String(length=16), nullable=True),
        sa.Column('error_code', sa.String(length=32), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=False, default=3),
        sa.Column('actor_id', sa.String(length=64), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_tasks_device_id'), 'tasks', ['device_id'], unique=False)
    op.create_index(op.f('ix_tasks_sn'), 'tasks', ['sn'], unique=False)
    op.create_index(op.f('ix_tasks_station_id'), 'tasks', ['station_id'], unique=False)
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
    op.create_index(op.f('ix_tasks_workorder_id'), 'tasks', ['workorder_id'], unique=False)
    
    # 3. station table (工位信息)
    op.create_table('stations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('station_id', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('line_code', sa.String(length=32), nullable=True),
        sa.Column('area_code', sa.String(length=32), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False, default='idle'),
        sa.Column('mode', sa.String(length=16), nullable=False, default='manual'),
        sa.Column('current_task_id', sa.String(length=64), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('resource_state', sa.JSON(), nullable=True),
        sa.Column('alarm_state', sa.JSON(), nullable=True),
        sa.Column('mounted_devices', sa.JSON(), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('station_id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_stations_area_code'), 'stations', ['area_code'], unique=False)
    op.create_index(op.f('ix_stations_current_task_id'), 'stations', ['current_task_id'], unique=False)
    op.create_index(op.f('ix_stations_line_code'), 'stations', ['line_code'], unique=False)
    op.create_index(op.f('ix_stations_status'), 'stations', ['status'], unique=False)
    
    # 4. device table (设备信息)
    op.create_table('devices',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('device_id', sa.String(length=64), nullable=False),
        sa.Column('station_id', sa.String(length=64), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('device_type', sa.String(length=32), nullable=True),
        sa.Column('protocol', sa.String(length=32), nullable=True),
        sa.Column('connect_status', sa.String(length=16), nullable=False, default='disconnected'),
        sa.Column('status', sa.String(length=16), nullable=False, default='idle'),
        sa.Column('is_connected', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_busy', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_heartbeat_alive', sa.Boolean(), nullable=False, default=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('calibration_info', sa.JSON(), nullable=True),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('device_id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_devices_connect_status'), 'devices', ['connect_status'], unique=False)
    op.create_index(op.f('ix_devices_device_type'), 'devices', ['device_type'], unique=False)
    op.create_index(op.f('ix_devices_station_id'), 'devices', ['station_id'], unique=False)
    op.create_index(op.f('ix_devices_status'), 'devices', ['status'], unique=False)
    
    # 5. alarm table (告警信息)
    op.create_table('alarms',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('alarm_id', sa.String(length=64), nullable=False),
        sa.Column('alarm_code', sa.String(length=64), nullable=True),
        sa.Column('alarm_level', sa.String(length=16), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False, default='active'),
        sa.Column('occurred_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('task_id', sa.String(length=64), nullable=True),
        sa.Column('station_id', sa.String(length=32), nullable=True),
        sa.Column('device_id', sa.String(length=64), nullable=True),
        sa.Column('workorder_id', sa.String(length=64), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('alarm_id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_alarms_alarm_code'), 'alarms', ['alarm_code'], unique=False)
    op.create_index(op.f('ix_alarms_alarm_level'), 'alarms', ['alarm_level'], unique=False)
    op.create_index(op.f('ix_alarms_device_id'), 'alarms', ['device_id'], unique=False)
    op.create_index(op.f('ix_alarms_occurred_at'), 'alarms', ['occurred_at'], unique=False)
    op.create_index(op.f('ix_alarms_station_id'), 'alarms', ['station_id'], unique=False)
    op.create_index(op.f('ix_alarms_status'), 'alarms', ['status'], unique=False)
    op.create_index(op.f('ix_alarms_task_id'), 'alarms', ['task_id'], unique=False)
    op.create_index(op.f('ix_alarms_workorder_id'), 'alarms', ['workorder_id'], unique=False)
    
    # 6. report table (测试报告 - 最关键工业追溯)
    op.create_table('reports',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('report_id', sa.String(length=64), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=True),
        sa.Column('workorder_id', sa.String(length=64), nullable=True),
        sa.Column('sn', sa.String(length=128), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, default='draft'),
        sa.Column('result', sa.String(length=16), nullable=True),
        sa.Column('task_snapshot', sa.JSON(), nullable=True),
        sa.Column('station_snapshot', sa.JSON(), nullable=True),
        sa.Column('device_snapshots', sa.JSON(), nullable=True),
        sa.Column('test_records', sa.JSON(), nullable=True),
        sa.Column('alarm_snapshots', sa.JSON(), nullable=True),
        sa.Column('software_version', sa.JSON(), nullable=True),
        sa.Column('operator_info', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_reports_result'), 'reports', ['result'], unique=False)
    op.create_index(op.f('ix_reports_sn'), 'reports', ['sn'], unique=False)
    op.create_index(op.f('ix_reports_status'), 'reports', ['status'], unique=False)
    op.create_index(op.f('ix_reports_task_id'), 'reports', ['task_id'], unique=False)
    op.create_index(op.f('ix_reports_workorder_id'), 'reports', ['workorder_id'], unique=False)
    
    # 7. test_record table (测试记录)
    op.create_table('test_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('report_id', sa.String(length=64), nullable=True),
        sa.Column('step', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('value_type', sa.String(length=16), nullable=True),
        sa.Column('value_raw', sa.Text(), nullable=True),
        sa.Column('expected', sa.Text(), nullable=True),
        sa.Column('tolerance', sa.Text(), nullable=True),
        sa.Column('is_pass', sa.Boolean(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('record_id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_test_records_report_id'), 'test_records', ['report_id'], unique=False)
    
    # 8. report_attachment table (报告附件)
    op.create_table('report_attachments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('attachment_id', sa.String(length=64), nullable=False),
        sa.Column('report_id', sa.String(length=64), nullable=True),
        sa.Column('type', sa.String(length=64), nullable=True),
        sa.Column('filename', sa.String(length=256), nullable=True),
        sa.Column('file_path', sa.String(length=512), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('upload_time', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('attachment_id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_report_attachments_report_id'), 'report_attachments', ['report_id'], unique=False)


def downgrade():
    """Downgrade to previous revision - drops all tables"""
    
    # 删除所有表（按依赖关系倒序）
    op.drop_table('report_attachments')
    op.drop_table('test_records')
    op.drop_table('reports')
    op.drop_table('alarms')
    op.drop_table('devices')
    op.drop_table('stations')
    op.drop_table('tasks')
    op.drop_table('work_orders')