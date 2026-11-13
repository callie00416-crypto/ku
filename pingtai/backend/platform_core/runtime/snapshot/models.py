"""
快照相关数据模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class SnapshotMetadata:
    """快照元数据"""
    snapshot_id: str
    created_at: datetime
    size_bytes: int
    runtime_version: str
    platform_info: str
    consistency_checksum: str


@dataclass
class RecoveryResult:
    """恢复结果"""
    success: bool
    snapshot_id: str
    recovery_time: datetime
    errors: list
    warnings: list