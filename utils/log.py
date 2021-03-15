"""
初始化日志模块

%(asctime)s - [%(filename)s/%(funcName)s()] - [%(levelname)s] - %(message)s
"""
import logging


def init_log(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    log = logging.getLogger('script log')
    return log