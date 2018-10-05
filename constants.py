# coding=utf-8

# 当前服务的版本
from tools.SYSTEM.config_ import read_dict_config
from tools.EXT.entity import Model
from tools.SYSTEM.logger_ import get_logger

# 配置文件路径
config_path = './server.conf'
config = read_dict_config(config_path)
config_obj = Model(config)

def _for(d):
    for k in d.keys():
        if type(d[k]) <> dict:
            print '{}:{}'.format(k, d[k])
        else:
            _for(d[k])

def exception(s):
    logger.exception()

def err(s):
    logger.error(s)
    print s

def out(s):
    logger.info(s)
    print(s)

logpath = config_obj.LOGGER.server_logger_path.value
level = config_obj.LOGGER.server_logger_level.value
logger = get_logger('server', logpath, level)

if __name__ == "__main__":
    _for(config)
