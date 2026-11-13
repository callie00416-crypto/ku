"""
死锁检测器
"""
import asyncio
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Set, Optional


class DeadlockDetector:
    """死锁检测器"""
    
    def __init__(self, check_interval: int = 30, timeout_threshold: int = 120):
        self.check_interval = check_interval
        self.timeout_threshold = timeout_threshold
        self.logger = logging.getLogger(__name__)
        self.resource_locks: Dict[str, Dict] = {}  # 资源锁信息
        self.waiting_chains: Dict[str, Dict] = {}  # 等待链信息
        self.lock = threading.RLock()
        self.detector_task = None
        self.is_active = False
        
    def acquire_resource(self, resource_id: str, owner_id: str):
        """申请资源"""
        with self.lock:
            if resource_id not in self.resource_locks:
                self.resource_locks[resource_id] = {
                    'holder': owner_id,
                    'acquired_at': time.time(),
                    'waiters': set()
                }
                self.logger.debug(f"资源 {resource_id} 被 {owner_id} 获得")
            else:
                # 添加到等待者列表
                self.resource_locks[resource_id]['waiters'].add(owner_id)
                self.waiting_chains[owner_id] = {
                    'waiting_for': resource_id,
                    'since': time.time()
                }
                self.logger.debug(f"{owner_id} 等待资源 {resource_id}")
                
    def release_resource(self, resource_id: str, owner_id: str):
        """释放资源"""
        with self.lock:
            if resource_id in self.resource_locks:
                lock_info = self.resource_locks[resource_id]
                if lock_info['holder'] == owner_id:
                    # 移除持有者
                    if lock_info['waiters']:
                        # 将第一个等待者设为新的持有者
                        new_holder = lock_info['waiters'].pop()
                        lock_info['holder'] = new_holder
                        lock_info['acquired_at'] = time.time()
                        if new_holder in self.waiting_chains:
                            del self.waiting_chains[new_holder]
                        self.logger.debug(f"资源 {resource_id} 转移给 {new_holder}")
                    else:
                        # 没有等待者，删除锁记录
                        del self.resource_locks[resource_id]
                        self.logger.debug(f"资源 {resource_id} 已释放")
                        
    async def start_detection(self):
        """开始检测"""
        if self.is_active:
            return
            
        self.is_active = True
        self.detector_task = asyncio.create_task(self._detection_loop())
        self.logger.info("死锁检测已启动")
        
    async def _detection_loop(self):
        """检测循环"""
        while self.is_active:
            try:
                await self._detect_deadlocks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                self.logger.info("死锁检测已取消")
                break
            except Exception as e:
                self.logger.error(f"死锁检测错误: {e}")
                
    async def _detect_deadlocks(self):
        """检测死锁"""
        with self.lock:
            # 检查等待时间过长的资源
            current_time = time.time()
            timeouts = []
            
            for resource_id, lock_info in self.resource_locks.items():
                wait_duration = current_time - lock_info['acquired_at']
                if wait_duration > self.timeout_threshold:
                    # 检查是否有循环等待
                    if self._has_circular_wait(resource_id, lock_info['holder']):
                        timeouts.append((resource_id, lock_info))
                        
            # 处理超时和死锁
            for resource_id, lock_info in timeouts:
                self.logger.warning(f"检测到潜在死锁或长时间等待: "
                                  f"资源 {resource_id}, 持有者 {lock_info['holder']}, "
                                  f"已等待 {wait_duration:.2f}s")
                await self._resolve_deadlock(resource_id, lock_info)
                
    def _has_circular_wait(self, start_resource: str, start_owner: str) -> bool:
        """检查是否存在循环等待"""
        # 简化的循环检测算法
        visited = set()
        current = start_resource
        
        while current in self.resource_locks:
            lock_info = self.resource_locks[current]
            holder = lock_info['holder']
            
            if holder in visited:
                return True  # 发现循环
            visited.add(holder)
            
            # 查找该持有者正在等待的资源
            next_resource = None
            for res_id, res_info in self.resource_locks.items():
                if holder in res_info.get('waiters', set()):
                    next_resource = res_id
                    break
                    
            if next_resource is None or next_resource == current:
                break
            current = next_resource
            
        return False
        
    async def _resolve_deadlock(self, resource_id: str, lock_info: Dict):
        """解决死锁"""
        self.logger.warning(f"尝试解决死锁: {resource_id}")
        
        # 简单策略：强制释放资源
        # 在实际应用中，这里可能需要更复杂的恢复逻辑
        with self.lock:
            if resource_id in self.resource_locks:
                holder = lock_info['holder']
                waiters = lock_info.get('waiters', set()).copy()
                
                # 强制释放资源
                del self.resource_locks[resource_id]
                self.logger.warning(f"强制释放资源 {resource_id}，原持有者: {holder}")
                
                # 通知等待者资源已释放（可能需要重新申请）
                for waiter in waiters:
                    if waiter in self.waiting_chains:
                        del self.waiting_chains[waiter]
                        
    def get_status(self) -> Dict:
        """获取检测器状态"""
        with self.lock:
            return {
                'active': self.is_active,
                'resource_count': len(self.resource_locks),
                'waiting_chains_count': len(self.waiting_chains),
                'resource_locks': {
                    k: {
                        'holder': v['holder'],
                        'waiters': list(v['waiters']),
                        'held_duration': time.time() - v['acquired_at']
                    } for k, v in self.resource_locks.items()
                }
            }
            
    async def stop_detection(self):
        """停止检测"""
        self.is_active = False
        if self.detector_task:
            self.detector_task.cancel()
            try:
                await self.detector_task
            except asyncio.CancelledError:
                pass
        self.logger.info("死锁检测已停止")