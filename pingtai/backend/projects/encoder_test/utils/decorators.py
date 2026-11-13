"""
装饰器工具
"""
import time
import functools
from typing import Callable, Any


class TimeoutError(Exception):
    """超时异常"""
    pass


def timer(func: Callable) -> Callable:
    """
    计时装饰器
    
    Args:
        func: 被装饰的函数
        
    Returns:
        包装后的函数
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            duration = end_time - start_time
            print(f"[TIMER] {func.__name__} executed in {duration:.4f} seconds")
    return wrapper


def call_with_timeout(func: Callable, timeout: float, *args, **kwargs) -> Any:
    """
    带超时的函数调用
    
    Args:
        func: 要调用的函数
        timeout: 超时时间（秒）
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        函数返回值
        
    Raises:
        TimeoutError: 超时异常
    """
    import threading
    
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]
