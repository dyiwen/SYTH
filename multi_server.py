#!/usr/bin/env python
# encoding: utf-8


import os, json, time, traceback
import redis
#from sqlservice import *
from sql_test import *
from tools.SYSTEM.os_ import *
from tools.SYSTEM.threading_ import  *
from tools.EXT.filter import Dicomfilter
from pulldata import *
from constants import config_obj, out, err
from multiprocessing import cpu_count,Process,JoinableQueue

from dcmlib.desensitize import desensitize_dir,is_not_desensitized

CNT = 1 

def get_request_json(patid, image_path, save_path):
    """
    生成请求dl server分析的json格式
    :param patid: 影像号
    :param path: 本地路径
    :return:
    """
    hjson = {}
    hjson['patid']= patid
    hjson['image_path']= image_path
    hjson['save_path']= save_path
    return hjson

def send_analysis_request(redis_client, channel, hjson):
    """
    通过redis，向dl server发送分析指定检查号的DICOM文件夹命令
    :param redis_client:
    :param channel:
    :param hjson:
    """
    redis_client.publish(channel, json.dumps(hjson))


def service(redis_client, channel, patient,TEST):    #patient : ['',[,,,,]]
    """
    预测当前病人
    :param redis_client:
    :param channel:
    :param patient:
    """
    try:
        patient_id = patient[0]
        out("start download image for patid {}".format(patient_id))

        # 正式使用改成True
        if True:
            outpath = os.path.join(config_obj.STORE.dicom_store.value, patient_id)  # 文件存储地址
            save_path = os.path.join(config_obj.STORE.image_store.value, patient_id)  # 预测结果保存路径
            dicompath_list = patient[1]             # pid ---- ['','',''...]
                                   
            #四种取病人dicom方式，四选一
            #---------------------------------------------------------------------------------------------
            # if True:
            #     dicompath_list = patient[1]
            #     for dicompath in dicompath_list:
            #         out_path = os.path.join(outpath,dicompath.split('/')[2])
            #         file_number = ftp_download(config_obj.FTP, dicompath, out_path)  # FTP 下载病人dicom
            #         #out('{}脱敏完成'.format(os.path.join(out_path.split('/')[-2],out_path.split('/')[-1])))
                    # if os.path.exists(out_path) and file_number > 0:
                    #     out("{} 共下载图像 {} 张".format(patient_id, file_number))
                    #     # gdcmconv(outpath) #解压dicom 
                    #     #desensitize_dir(out_path)
                    #     out("脱敏完成 {} ".format(out_path))
                    #     out('是否脱敏:'+str(is_not_desensitized(out_path)))
                    #     if is_not_desensitized(out_path):
                    #         redis_client.set(patient_id, out_path, ex=24*60*60*2)
                    #         hjson = get_request_json(patient_id, out_path, save_path)
                    #         send_analysis_request(redis_client, channel, hjson) # 发信预测信号到dlserver
                    #     else:
                    #         out("脱敏失败 {} ".format(out_path))
                    #     out("发送病人 {} 预测信号到频道 {} 成功".format(patient_id,channel))
                    # elif os.path.exists(out_path) and file_number == 0:
                    #     pass
                    # elif not os.path.exists(out_path):
                    #     pass
                    # else:
                    #     out("the sending channl failed ,download image count {} patid is {}".format(file_number, out_path))
                    #     err(traceback.format_exc())
            #----------------------------------------------------------------------------------------------
            if True:
                for dicompath in dicompath_list:                                             # .....local/date/CT/serid
                    out_path = os.path.join(outpath,dicompath.split('/')[7])               #/media/tx-deepocean/Data/DICOMS/CT/pid/serid
                    file_number = cp_mount(dicompath, out_path)  # copy 挂载PACS存储
                    #out('{}脱敏完成'.format(os.path.join(out_path.split('/')[-2],out_path.split('/')[-1])))
                    if os.path.exists(out_path) and file_number > 0:
                        out("{} 共下载图像 {} 张".format(patient_id, file_number))
                        # gdcmconv(outpath) #解压dicom 
                        #desensitize_dir(out_path)
                        out("脱敏完成 {} ".format(out_path))
                        out('是否脱敏:'+str(is_not_desensitized(out_path)))
                        if is_not_desensitized(out_path):
                            redis_client.set(patient_id, out_path, ex=24*60*60*2)
                            hjson = get_request_json(patient_id, out_path, save_path)
                            send_analysis_request(redis_client, channel, hjson) # 发信预测信号到dlserver
                        else:
                            out("脱敏失败 {} ".format(out_path))
                        out("发送病人 {} 预测信号到频道 {} 成功".format(patient_id,channel))
                    elif os.path.exists(out_path) and file_number == 0:
                        pass
                    elif not os.path.exists(out_path):
                        pass
                    else:
                        out("the sending channl failed ,download image count {} patid is {}".format(file_number, out_path))
                        err(traceback.format_exc())

    except:
        out("service run err {}".format(patient_id))
        err(traceback.format_exc())

def Worker(redis_client,TEST):
    while True:
        item = q.get()
        if item is None:
            break
        service(redis_client,item[0],item[1],TEST)
        q.task_done()

def Multi(redis_client, channel, patient_list,TEST):
    """
    开始获取符合条件的病人，进行预测
    :param redis_client:
    :param channel:
    :return:
    """
    try:
        starttime = time.time()
        cpuCount = cpu_count()  # 计算本机CPU核数
        #cpuCount = 1
        print 'cpuCount is :',cpuCount
        multiprocessing = []

        for i in xrange(0, cpuCount):  # 创建cpu_count()个进程
            p = Process(target=Worker, args=(redis_client, TEST))
            p.daemon = True
            p.start()
            multiprocessing.append(p)

        global CNT
        for i in range(len(patient_list)):
            q.put([channel+str(CNT%channelCount), patient_list[i]])
            CNT += 1
        q.join()

        for i in xrange(0, cpuCount):
            q.put(None)
        for p in multiprocessing:
            p.join()

        elapsed = (time.time() - starttime)
        out("cpuCount: {} Finished with time:{}".format(cpuCount, elapsed))

    except:
        out("Multi run error")
        err(traceback.print_exc())

#--------------------------------------------------------------------------------------------------
def get_patient_dicom_path(redis_client, patient_list):
    """
    遍历患者集合，匹配对应DICOM路径
    :param patient_list
    :return new_patient_list  [[patient_id,[dicom_path,...]]...]
    """
    patient_id_list = []
    # print '----',len(patient_list)
    for patient_id in patient_list:
        if not redis_client.exists(patient_id):
            patient_id_list.append(patient_id)
    new_patient_list = select_path_from_db2(patient_id_list)
    # print '---',len(new_patient_list)
    # print new_patient_list
    return new_patient_list
#---------------------------------------------------------------------------------------------------

def main(redis_client, channel,TEST):
    try:
        #patient_list = select_id_list_from_study_status(TEST)  # 查询patient （医院RIS）
        out('开始数据库查询，请稍后....')
        patient_list = select_id_list_from_sqls(TEST)
        patient_list = get_patient_dicom_path(redis_client, patient_list)[:100] # 查询patient dicom path (医院pacs)
        out('从数据库查到 {} 位病人'.format(len(patient_list)))

        if len(patient_list) > 0:
            Multi(redis_client, channel, patient_list,TEST) #start
    except:
        out("main run error")
        err(traceback.print_exc())

if __name__ == '__main__':
    mkdir_recursive('./log')

    try:
        rcon = redis.Redis()
        channel = "CT"
        channelCount = 4
        """
        receive 接收预测服务返回
        """
        while True:
            out("server run start !")
            q = JoinableQueue()
            main(rcon, channel,TEST=False)  # 测试两分钟无误后修改为False
            time.sleep(float(config_obj.OTHER.server_sleep.value))

    except:
        out("run error")
        out(traceback.print_exc())
