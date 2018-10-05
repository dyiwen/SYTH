# coding=utf-8
"""
系统工具
"""
import errno
import os


def mkdir_recursive(path, mode=0777):
    """
    等同于 mkdir -p <path>
    且如果文件夹存在不报错
    :param path: str 目录路径
    :param mode: int 目录权限
    """
    try:
        os.makedirs(path, mode=mode)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def purge_empty_dir(path, depth=0):
    """
    递归删除top_path下的空目录
    :param path: str 目录路径
    :param depth: int 深度
    """
    path = os.path.abspath(path)
    children = os.listdir(path)
    for c in children:
        c = os.path.join(path, c)
        if not os.path.isdir(c):
            continue
        purge_empty_dir(c, depth + 1)
    if not os.listdir(path) and depth > 0:
        os.rmdir(path)
