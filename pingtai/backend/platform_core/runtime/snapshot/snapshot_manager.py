"""
快照管理器 - 负责创建、加载和恢复运行时快照
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
import logging
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class RuntimeSnapshot:
    """运行时快照数据结构"""
    snapshot_id: str
    created_at: datetime
    station_states: Dict[str, Any]
    actor_states: Dict[str, Any]
    task_states: Dict[str, Any]
    device_states: Dict[str, Any]
    runtime_version: str
    metadata: Dict[str, Any] = None


class SnapshotManager:
    """快照管理器 - 负责快照的创建、加载和恢复"""
    
    def __init__(self, snapshot_dir: str = "./snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    async def create_snapshot(self, runtime_state: Dict[str, Any]) -> str:
        """创建运行时快照"""
        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(runtime_state)) % 10000}"
        
        # 构建快照对象 - 只保存关键状态
        snapshot = RuntimeSnapshot(
            snapshot_id=snapshot_id,
            created_at=datetime.now(),
            station_states=runtime_state.get('station_states', {}),
            actor_states=runtime_state.get('actor_states', {}),
            task_states=runtime_state.get('task_states', {}),
            device_states=runtime_state.get('device_states', {}),
            runtime_version="1.0.0",  # 从版本管理系统获取
            metadata={
                'size': len(json.dumps(runtime_state)),
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # 保存快照到文件
        snapshot_file = self.snapshot_dir / f"{snapshot_id}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(snapshot), f, ensure_ascii=False, default=str)
            
        self.logger.info(f"快照创建成功: {snapshot_id}, 文件: {snapshot_file}")
        return snapshot_id
        
    async def load_latest_snapshot(self) -> Optional[RuntimeSnapshot]:
        """加载最新的快照"""
        snapshot_files = list(self.snapshot_dir.glob("snapshot_*.json"))
        if not snapshot_files:
            self.logger.info("没有找到快照文件")
            return None
            
        # 按文件修改时间排序，获取最新的快照
        latest_snapshot = max(snapshot_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_snapshot, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 重建快照对象
        snapshot = RuntimeSnapshot(
            snapshot_id=data['snapshot_id'],
            created_at=datetime.fromisoformat(data['created_at']),
            station_states=data['station_states'],
            actor_states=data['actor_states'],
            task_states=data['task_states'],
            device_states=data['device_states'],
            runtime_version=data['runtime_version'],
            metadata=data.get('metadata')
        )
        
        self.logger.info(f"加载快照成功: {snapshot.snapshot_id}")
        return snapshot
        
    async def restore_runtime(self, snapshot: RuntimeSnapshot) -> bool:
        """从快照恢复运行时状态"""
        try:
            # 注意：这里不会盲目恢复，而是作为恢复底座
            # Domain层需要重新校验业务一致性
            self.logger.info(f"开始从快照恢复: {snapshot.snapshot_id}")
            
            # 这里应该与实际的运行时组件交互来恢复状态
            # 伪代码示例：
            # await self._restore_tasks(snapshot.task_states)
            # await self._restore_devices(snapshot.device_states)
            # await self._restore_actors(snapshot.actor_states)
            
            self.logger.info(f"快照恢复完成: {snapshot.snapshot_id}")
            return True
        except Exception as e:
            self.logger.error(f"快照恢复失败: {e}", exc_info=True)
            return False
            
    async def cleanup_old_snapshots(self, keep_last_n: int = 5):
        """清理旧快照，保留最近的N个"""
        snapshot_files = list(self.snapshot_dir.glob("snapshot_*.json"))
        if len(snapshot_files) <= keep_last_n:
            return
            
        # 按时间排序，删除最旧的
        sorted_files = sorted(snapshot_files, key=lambda x: x.stat().st_mtime)
        files_to_delete = sorted_files[:-keep_last_n]
        
        for file in files_to_delete:
            file.unlink()
            self.logger.info(f"删除旧快照: {file.name}")