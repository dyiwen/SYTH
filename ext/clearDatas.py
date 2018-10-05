# -*- coding: utf-8 -*-

import sys, os, time, traceback, shutil
sys.path.append('/home/tx-deepocean/Infervision/tx_hospital_interface')

class Clear(object):
    """
    清理历史数据
    """
    def __init__(self):
        self.current_mon = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    def out(self, s):
        sys.stdout.write('\b\r {}'.format(s))
        sys.stdout.flush()
    
    def timeformat(self, s):
        """
        input 年-月-日 type str
        return: 返回天数 type int
        """
        timelist = s.split("-")
        assert len(timelist) == 3
        return int(timelist[0])*12*30 + int(timelist[1])*30 + int(timelist[2])    
    
    def delete_historical_data(self, path, days_ago= 15):
        """
        删除指定时间前的数据
        :param path 数据路径
        :param days_ago 前几天 type int
        """
        self.count = 0
        for folder in os.listdir(path):
            folderpath = os.path.join(path, folder)
            folder_mon = time.strftime('%Y-%m-%d',time.localtime(os.path.getmtime(folderpath)))
            
            if(self.timeformat(self.current_mon) - self.timeformat(folder_mon)) > days_ago:
                shutil.rmtree(folderpath)
                self.count += 1
                self.out("delete count:{}".format(self.count))


if __name__ == "__main__":
    from tools.SYSTEM.logger_ import get_logger
    from constants import config
    
    try:
        LOGGER_config = config['LOGGER']
        logger = get_logger('clear',LOGGER_config['clear_logger_path'])
        store = config['STORE']
        clear = Clear()
        for key in store.keys():
            clear.delete_historical_data(store[key], days_ago = 15)
            logger.info('{} |rm count:{}'.format(store[key], clear.count))
    except:
        logger.error(traceback.print_exc())
        print traceback.print_exc()
