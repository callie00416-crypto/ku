"""
快照序列化器 - 负责快照数据的序列化和反序列化
"""
import json
from typing import Any, Dict
import pickle
import dill  # 更强大的序列化库
import logging
from datetime import datetime


class SnapshotSerializer:
    """快照序列化器 - 负责快照数据的序列化和反序列化"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def serialize(self, obj: Any) -> str:
        """序列化对象为字符串"""
        try:
            # 使用JSON进行序列化，确保可读性和兼容性
            return json.dumps(obj, ensure_ascii=False, default=str)
        except Exception as e:
            self.logger.error(f"序列化失败: {e}", exc_info=True)
            raise
            
    def deserialize(self, data: str) -> Any:
        """从字符串反序列化对象"""
        try:
            return json.loads(data)
        except Exception as e:
            self.logger.error(f"反序列化失败: {e}", exc_info=True)
            raise
            
    def validate_serializable(self, obj: Any) -> bool:
        """验证对象是否可序列化"""
        try:
            json.dumps(obj, ensure_ascii=False, default=str)
            return True
        except:
            return False