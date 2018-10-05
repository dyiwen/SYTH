# coding=utf-8
import logging


def get_logger(name, path, level=logging.INFO, mode = 'a'):
    """
    获取logger
    :param name: str 名称
    :param path: str 路径
    :param level: logging.LEVEL 日志级别
    :return: logging.Logger 日志对象
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(path)
    handler.mode = mode
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
