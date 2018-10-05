# coding=utf-8
import ConfigParser


def write_dict_config(config, path):
    """
    把字段字典配置写入
    :param config: dict 配置字典
        config = {
            'section': {
                'option': 'value',
                ...
            },
            ...
        }
    :param path: str 写入的文件路径
    """
    cf = ConfigParser.ConfigParser()
    for section, d in config.iteritems():
        for option, value in d.iteritems():
            if not cf.has_section(section):
                cf.add_section(section)
            cf.set(section, option, value)
    with open(path, 'w') as f:
        cf.write(f)


def read_dict_config(path):
    """
    读取配置, 返回字典
    :param path: str 配置文件路径
    :return: dict 配置字典
    """
    config_dict = {}
    cf = ConfigParser.ConfigParser()
    cf.read(path)
    sections = cf.sections()
    for s in sections:
        config_dict.setdefault(s, {})
        for o in cf.options(s):
            config_dict[s][o] = cf.get(s, o)
    return config_dict


if __name__ == '__main__':
    path = '../server.conf'
    config = {
        'SCP': {
            'ae_title': 'TXPACS',
            'port': 11112,
            'store_path': './store/',
            'series_update_limit': 60,
        },
        'DB': {
            'db': 'txpacs',
            'user': 'tx',
            'password': 'txnb',
            'host': 'localhost',
        }
    }
    write_dict_config(config, path)
