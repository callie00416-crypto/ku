"""
日志工具
"""
import logging


def get_logger(name: str = None):
    """
    获取logger实例
    
    Args:
        name: logger名称
        
    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
