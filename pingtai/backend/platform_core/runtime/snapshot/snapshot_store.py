"""
快照存储 - 负责快照的持久化存储
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
import logging


class SnapshotStore:
    """快照存储 - 负责快照的持久化存储"""
    
    def __init__(self, base_dir: str = "./snapshots"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    async def save_snapshot(self, snapshot_id: str, data: Dict[str, Any]) -> bool:
        """保存快照到存储"""
        try:
            snapshot_file = self.base_dir / f"{snapshot_id}.json"
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, default=str)
            self.logger.info(f"快照保存成功: {snapshot_id}")
            return True
        except Exception as e:
            self.logger.error(f"快照保存失败: {e}", exc_info=True)
            return False
            
    async def load_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """从存储加载快照"""
        try:
            snapshot_file = self.base_dir / f"{snapshot_id}.json"
            if not snapshot_file.exists():
                return None
                
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"快照加载成功: {snapshot_id}")
            return data
        except Exception as e:
            self.logger.error(f"快照加载失败: {e}", exc_info=True)
            return None
            
    async def list_snapshots(self) -> list:
        """列出所有快照"""
        snapshots = []
        for file in self.base_dir.glob("snapshot_*.json"):
            stat = file.stat()
            snapshots.append({
                'id': file.stem,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'path': str(file)
            })
        return sorted(snapshots, key=lambda x: x['modified'], reverse=True)
        
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """删除指定快照"""
        try:
            snapshot_file = self.base_dir / f"{snapshot_id}.json"
            if snapshot_file.exists():
                snapshot_file.unlink()
                self.logger.info(f"快照删除成功: {snapshot_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"快照删除失败: {e}", exc_info=True)
            return False