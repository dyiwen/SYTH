#!/usr/bin/env python
# encoding: utf-8

import sys, os, time, traceback, shutil

import subprocess
from subprocess import CalledProcessError

import zipfile

from tools.RSYNC.FTP_ import FTPrsync, RsyncExtra
from tools.SYSTEM.threading_ import pooled
from constants import config, config_obj, out, err, exception

import dicom, shutil
from dcmlib.desensitize import *


def unzip(source):
    """
    解压提取
    :param source: 文件路径
    :return:
    """
    try:
        with zipfile.ZipFile(source, "r") as zf:
            zf.extractall()
            zf.close()
    except:
        out("解压失败 {}".format(source))
        err(traceback.print_exc())

def gdcmconv(source):
    """
    gdcm 解压dicom文件
    :param source: 数据源，dicom目录
    """
    for rootpath, folder, filenames in os.walk(source):
        for filename in filenames:
            filepath = os.path.join(rootpath, filename)
            cmd = "gdcmconv -w {} {}".format(filepath, filepath)
            os.system(cmd)
#------------------------------------------------------------------------------
def isnotdicom(s):
    try:
        ds = dicom.read_file(s)
    except:
        try:          
            os.remove(s)
        except:
            out('没有该路径 {}'.format(s))
            warn(traceback.format_exc())
        return True

def isnotslice(s):
    try:
        ds = dicom.read_file(s)
        ds.SliceThickness
        a = True
    except:
        os.remove(s)
        a = False
    return a

def filter_slice_protocol(destination):
    if os.path.exists(destination):
        dicom_path_list = [os.path.join(destination,i) for i in os.listdir(destination)]
        for dicom_path in dicom_path_list:
            ds = dicom.read_file(dicom_path)
            try:
                if isnotslice(dicom_path):
                    if ds.SliceThickness >= 2 or ds.SliceThickness < 0.625:
                        os.remove(dicom_path)
                        #print True
                    elif ('Head' in ds.ProtocolName and ds.ProtocolName != 'Head_Chest' and ds.ProtocolName != '02_HeadRoutine') or 'pelvis' in ds.ProtocolName or 'pfos' in ds.ProtocolName or 'Head' in ds.SeriesDescription or ds.ProtocolName == '1.8 HCTA' or ds.SeriesDescription == 'Processed Images' or 'Foot' in ds.ProtocolName or ds.SeriesDescription == '1.25mm' or ds.ProtocolName == '5.13 SnapShot Segment (test bolus)':       
                    #elif 'Head' in ds.ProtocolName or ds.ProtocolName == '1.8 HCTA' or ds.SeriesDescription == 'Processed Images' or 'Foot' in ds.ProtocolName or ds.SeriesDescription == '1.25mm':
                        os.remove(dicom_path)
                        #print 'Head in'
                    #out('{} 过滤掉头部图像'.format(destination[35:]))
                else:
                    pass
            except:
                err(traceback.format_exc())
        if len(os.listdir(destination)) == 0:
            print True
            os.rmdir(destination)


    # if os.path.exists(destination):
    #     dicom_path = os.path.join(destination,os.listdir(destination)[0])
    #     #print dicom_path
    #     ds = dicom.read_file(dicom_path)
    #     if ds.SliceThickness >= 2:
    #         shutil.rmtree(destination)
    #     if 'Head' in ds.ProtocolName:
    #         shutil.rmtree(destination)
    #         out('{} 过滤掉头部图像'.format(destination[35:]))
    # else:
    #     out('{} 数量不足,已删除'.format(destination[35:]))


def filter_sop(destination):
    SOP_list = []
    for roots,dirs,files in os.walk(destination):
        for sop_path in files:
            print sop_path
            remove_path = os.path.join(roots,sop_path)
            try:
                ds = dicom.read_file(remove_path)
                #print ds.SOPInstanceUID
                remove_parts =  int(ds.SOPInstanceUID.split('.')[-2])
                if remove_parts not in SOP_list:
                    SOP_list.append(remove_parts)
            except: 
                print "Don't have SOPInstanceUID"
                traceback.print_exc()
                os.remove(remove_path)
    print SOP_list
    for remove_UID in files:
        remove_UID_path = os.path.join(roots,remove_UID)
        ds2 = dicom.read_file(remove_UID_path)
        if int(ds2.SOPInstanceUID.split('.')[-2]) != min(SOP_list):
            os.remove(remove_UID_path)

def filter_dicom(destination):
    filter_slice(destination)
    filter_sop(destination)


def re_name(destination):
    if os.path.exists(destination):
        dicom_list = os.listdir(destination)
        dicom_path_list = [os.path.join(destination,i) for i in dicom_list]
        for dicom_path in dicom_path_list:
            #print dicom_path
            os.rename(dicom_path,dicom_path.replace('JL','dcm'))


#------------------------------------------------------------------------------------

def ftp_download(obj, source, destination):
    """
    下载文件
    :param source: FTP文件路径
    :param destination: dicom存储路径
    :return: dicom个数
    """
    try:
        ftpsync = RsyncExtra(user=obj.username.value, pwd=obj.password.value, host=obj.host.value,
                             port=obj.port.value, timeout= float(obj.timeout.value))
        #ftpsync.func = unzip
        ftpsync.sync(source, destination,tree= False)
        gdcmconv(destination)
        re_name(destination)
        filter_slice_protocol(destination)
        desensitize_dir(destination)
    except:
        out("ftp下载病人影像失败 {}".format(source))
        out(traceback.format_exc())

    if os.path.exists(destination):
        return len(os.listdir(destination))
    else:
        return 0

#---------------------------------------------------------------------------------------
 
def cp_mount(source, destination):
    try:         # local..../date/CT/serid      /media/tx-deepocean/Data/DICOMS/CT/pid/serid
        if os.path.exists(destination) and len(os.listdir(destination)) == len(os.listdir(source)):
            print '已存在 {}'.format(destination)
        elif os.path.exists(destination) and len(os.listdir(destination)) != len(os.listdir(source)):
            cmd = 'rm -rf '+destination
            os.system(cmd)
        if os.path.exists(source) and not os.path.exists(destination):
            if len(os.listdir(source)) in range(70,999):
                shutil.copytree(source, destination)
                if len(os.listdir(destination)) != len(os.listdir(source)):
                    cmd = 'rm -rf '+destination
                    os.system(cmd)
                else:
                    gdcmconv(destination)
                    re_name(destination)
                    filter_slice_protocol(destination)
                    desensitize_dir(destination)
            else:
                print '数量不足 {}'.format(source)
        else:
            print '目录不存在 {}'.format(source)
    except:
        out('磁盘挂载下载失败 {}'.format(source))
        out(traceback.format_exc())

    if os.path.exists(destination):
        return len(os.listdir(destination))
    else:
        return 0
        

if __name__ == '__main__':
    ftp_download(config_obj.FTP,'20180919/CT/1.2.840.113619.2.334.3.1690329956.842.1536415462.160.3','/media/tx-deepocean/Data/DICOMS/wenti/head/69082052/1.2.840.113619.2.334.3.1690329956.842.1536415462.160.3')
    #filter_slice('/media/tx-deepocean/Data/DICOMS/CT/69108218/1.2.840.113619.2.334.3.1690329956.842.1536415434.149.4')


    # root = '/media/tx-deepocean/Data/DICOMS/test/07047952/1.2.840.113619.2.55.3.1690327908.79.1536922796.792.4'
    # is_not_desensitized(root)
    #filter_slice_protocol('/media/tx-deepocean/Data/DICOMS/wenti/head/69082052/1.2.840.113619.2.334.3.1690329956.842.1536415462.160.3')
