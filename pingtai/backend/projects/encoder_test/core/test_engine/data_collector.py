"""
数据采集模块 - 原始数据采集、缓存、结构化处理、实时上报、断网缓存
"""
import json
import time
import threading
import queue
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


@dataclass
class DataPoint:
    """数据点"""
    timestamp: float
    task_id: str
    station_id: int
    product_sn: str
    data_type: str  # angle, speed, torque, temperature, etc.
    value: float
    unit: str = ""
    quality: str = "good"  # good, bad, uncertain
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class DataBatch:
    """数据批次 - 用于批量上报"""
    batch_id: str
    task_id: str
    station_id: int
    product_sn: str
    data_points: List[DataPoint] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    uploaded: bool = False
    
    def add_point(self, point: DataPoint):
        """添加数据点"""
        self.data_points.append(point)
    
    def point_count(self) -> int:
        """数据点数量"""
        return len(self.data_points)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'batch_id': self.batch_id,
            'task_id': self.task_id,
            'station_id': self.station_id,
            'product_sn': self.product_sn,
            'data_points': [p.to_dict() for p in self.data_points],
            'created_at': self.created_at,
            'uploaded': self.uploaded
        }


class DataCollector:
    """数据采集器 - 支持实时采集、缓存、断网补传"""
    
    def __init__(self, cache_dir: str = "./data_cache", 
                 batch_size: int = 100,
                 upload_interval: float = 5.0,
                 max_cache_size: int = 10000):
        """
        Args:
            cache_dir: 缓存目录
            batch_size: 批量上报大小
            upload_interval: 上报间隔（秒）
            max_cache_size: 最大缓存数量
        """
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        self.upload_interval = upload_interval
        self.max_cache_size = max_cache_size
        
        # 数据队列
        self._data_queue = queue.Queue(maxsize=max_cache_size)
        
        # 缓存批次
        self._current_batch: Optional[DataBatch] = None
        self._batch_lock = threading.Lock()
        
        # 断网缓存
        self._offline_cache: List[DataBatch] = []
        self._is_online = True
        self._cache_lock = threading.Lock()
        
        # 上报回调
        self._upload_callback: Optional[Callable] = None
        
        # 上报线程
        self._upload_thread = None
        self._upload_running = False
        
        # 统计信息
        self._stats = {
            'total_collected': 0,
            'total_uploaded': 0,
            'total_failed': 0,
            'cache_count': 0
        }
        self._stats_lock = threading.Lock()
        
        # 确保缓存目录存在
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"数据采集器初始化完成 (缓存目录: {cache_dir}, 批量大小: {batch_size})")
    
    def set_upload_callback(self, callback: Callable):
        """
        设置数据上报回调
        
        Args:
            callback: 回调函数，接收 DataBatch 参数
        """
        self._upload_callback = callback
        logger.info("数据上报回调已设置")
    
    def set_online_status(self, online: bool):
        """
        设置网络状态
        
        Args:
            online: True=在线，False=离线
        """
        with self._cache_lock:
            self._is_online = online
        
        if online:
            logger.info("网络已恢复，开始补传离线数据")
            self._flush_offline_cache()
        else:
            logger.warning("网络断开，数据将缓存到本地")
    
    def collect(self, task_id: str, station_id: int, product_sn: str,
                data_type: str, value: float, unit: str = "",
                quality: str = "good", metadata: Dict[str, Any] = None):
        """
        采集数据点
        
        Args:
            task_id: 任务ID
            station_id: 工位ID
            product_sn: 产品SN码
            data_type: 数据类型
            value: 数据值
            unit: 单位
            quality: 数据质量
            metadata: 元数据
        """
        point = DataPoint(
            timestamp=time.time(),
            task_id=task_id,
            station_id=station_id,
            product_sn=product_sn,
            data_type=data_type,
            value=value,
            unit=unit,
            quality=quality,
            metadata=metadata or {}
        )
        
        try:
            self._data_queue.put_nowait(point)
            self._increment_stat('total_collected')
        except queue.Full:
            logger.error(f"数据队列已满，丢弃数据点: {data_type}={value}")
            self._increment_stat('total_failed')
        
        # 检查是否需要创建新批次
        with self._batch_lock:
            if self._current_batch is None or self._current_batch.point_count() >= self.batch_size:
                self._current_batch = DataBatch(
                    batch_id=f"batch_{int(time.time())}_{station_id}",
                    task_id=task_id,
                    station_id=station_id,
                    product_sn=product_sn
                )
            
            self._current_batch.add_point(point)
            
            # 批次已满，处理上报
            if self._current_batch.point_count() >= self.batch_size:
                self._process_batch(self._current_batch)
                self._current_batch = None
    
    def collect_batch(self, task_id: str, station_id: int, product_sn: str,
                      data_points: List[Dict[str, Any]]):
        """
        批量采集数据
        
        Args:
            task_id: 任务ID
            station_id: 工位ID
            product_sn: 产品SN码
            data_points: 数据点列表
        """
        for point_data in data_points:
            self.collect(
                task_id=task_id,
                station_id=station_id,
                product_sn=product_sn,
                data_type=point_data.get('data_type', 'unknown'),
                value=point_data.get('value', 0.0),
                unit=point_data.get('unit', ''),
                quality=point_data.get('quality', 'good'),
                metadata=point_data.get('metadata')
            )
    
    def _process_batch(self, batch: DataBatch):
        """
        处理数据批次
        
        Args:
            batch: 数据批次
        """
        if batch.point_count() == 0:
            return
        
        with self._cache_lock:
            if self._is_online:
                # 在线模式：直接上报
                self._upload_batch(batch)
            else:
                # 离线模式：缓存到本地
                self._offline_cache.append(batch)
                self._save_batch_to_disk(batch)
                self._increment_stat('cache_count')
                logger.debug(f"数据已缓存 (离线): {batch.batch_id}, 数据点: {batch.point_count()}")
    
    def _upload_batch(self, batch: DataBatch):
        """
        上报数据批次
        
        Args:
            batch: 数据批次
        """
        try:
            if self._upload_callback:
                self._upload_callback(batch)
            
            batch.uploaded = True
            self._increment_stat('total_uploaded')
            logger.debug(f"数据批次上报成功: {batch.batch_id}")
            
        except Exception as e:
            logger.error(f"数据批次上报失败: {batch.batch_id}, 错误: {e}")
            self._increment_stat('total_failed')
            
            # 上报失败，转入离线缓存
            with self._cache_lock:
                self._offline_cache.append(batch)
                self._save_batch_to_disk(batch)
    
    def _save_batch_to_disk(self, batch: DataBatch):
        """
        保存批次到磁盘
        
        Args:
            batch: 数据批次
        """
        try:
            cache_file = Path(self.cache_dir) / f"{batch.batch_id}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(batch.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存批次到磁盘失败: {e}")
    
    def _flush_offline_cache(self):
        """刷新离线缓存（网络恢复后调用）"""
        with self._cache_lock:
            batches_to_upload = self._offline_cache.copy()
            self._offline_cache.clear()
        
        for batch in batches_to_upload:
            try:
                self._upload_batch(batch)
                # 删除已上报的缓存文件
                cache_file = Path(self.cache_dir) / f"{batch.batch_id}.json"
                if cache_file.exists():
                    cache_file.unlink()
            except Exception as e:
                logger.error(f"补传离线数据失败: {batch.batch_id}, 错误: {e}")
                # 补传失败，重新加入缓存
                with self._cache_lock:
                    self._offline_cache.append(batch)
    
    def start_auto_upload(self):
        """启动自动上报线程"""
        if self._upload_running:
            return
        
        self._upload_running = True
        self._upload_thread = threading.Thread(target=self._auto_upload_loop, daemon=True)
        self._upload_thread.start()
        logger.info("自动上报线程已启动")
    
    def stop_auto_upload(self):
        """停止自动上报线程"""
        self._upload_running = False
        if self._upload_thread:
            self._upload_thread.join(timeout=5.0)
        logger.info("自动上报线程已停止")
    
    def _auto_upload_loop(self):
        """自动上报循环"""
        while self._upload_running:
            try:
                # 检查当前批次是否需要上报
                with self._batch_lock:
                    if self._current_batch and self._current_batch.point_count() > 0:
                        elapsed = time.time() - self._current_batch.created_at
                        if elapsed >= self.upload_interval:
                            self._process_batch(self._current_batch)
                            self._current_batch = None
                
                time.sleep(1.0)  # 每秒检查一次
                
            except Exception as e:
                logger.error(f"自动上报循环异常: {e}")
                time.sleep(1.0)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        with self._stats_lock:
            return self._stats.copy()
    
    def _increment_stat(self, key: str):
        """增加统计计数"""
        with self._stats_lock:
            self._stats[key] = self._stats.get(key, 0) + 1
    
    def get_pending_count(self) -> int:
        """获取待处理数据点数量"""
        return self._data_queue.qsize()
    
    def flush(self):
        """强制刷新所有缓存数据"""
        # 处理当前批次
        with self._batch_lock:
            if self._current_batch and self._current_batch.point_count() > 0:
                self._process_batch(self._current_batch)
                self._current_batch = None
        
        # 刷新离线缓存
        if self._is_online:
            self._flush_offline_cache()
        
        logger.info("数据采集器已刷新")
    
    def clear_cache(self):
        """清空缓存"""
        with self._cache_lock:
            self._offline_cache.clear()
        
        # 删除缓存文件
        cache_path = Path(self.cache_dir)
        if cache_path.exists():
            for file in cache_path.glob("*.json"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"删除缓存文件失败: {file}, 错误: {e}")
        
        logger.info("数据缓存已清空")
    
    def load_offline_cache_from_disk(self) -> List[DataBatch]:
        """从磁盘加载离线缓存"""
        batches = []
        cache_path = Path(self.cache_dir)
        
        if not cache_path.exists():
            return batches
        
        for json_file in cache_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                
                # 重建 DataBatch 对象
                batch = DataBatch(
                    batch_id=batch_data['batch_id'],
                    task_id=batch_data['task_id'],
                    station_id=batch_data['station_id'],
                    product_sn=batch_data['product_sn'],
                    created_at=batch_data.get('created_at', time.time()),
                    uploaded=batch_data.get('uploaded', False)
                )
                
                for point_data in batch_data.get('data_points', []):
                    point = DataPoint(**point_data)
                    batch.add_point(point)
                
                batches.append(batch)
                
            except Exception as e:
                logger.error(f"加载缓存文件失败: {json_file}, 错误: {e}")
        
        logger.info(f"从磁盘加载离线缓存: {len(batches)} 个批次")
        return batches
