# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 13:11:49 2017
重置/生成配置文件

"""

from tools.SYSTEM.config_ import write_dict_config

if __name__ == "__main__":
    print "reset config"
    
    path = './server.conf'
    config = {
        'SCP': {
            'ae_title': 'TXPACS',
            'port': 11112,
            'store_path': './store/',
            'series_update_limit': 60,
        },
        'TXDB': {
            'db': 'txdatas',
            'user': 'tx',
            'password': 'txnb',
            'host': 'localhost',
        },
        'LOGGER':{
            'server_logger_path': './log/watcher.log',
            'server_logger_level': 'DEBUG',
            'clear_logger_path': './log/clear.log',
            'clear_logger_level': 'DEBUG',
        },
        'FTP':{
            'host': '0.0.0.0',
            'port': 21,
            'timeout': 60,
            'username': 'ftp',
            'password': 'ftp',
            
        },
        'PULL':{
        'ae_title':'*               #本地ae title',
        'port':'11113               #本地ae port',
        'called_ae_host': '0.0.0.0  #called ae ip',
        'called_ae_port': '6789     #called ae port',
        'called_ae_title':'*        #called ae title',
        'key_index': '08, 05        #检索索引（patient id)'
        },
        'OTHER':{
            'server_sleep': 180,
            'save_path': '../../imageAccessServer/output/CT'
        }
    }
    write_dict_config(config, path)
