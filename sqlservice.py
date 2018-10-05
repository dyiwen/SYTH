#!/usr/bin/env python
# encoding: utf-8

from tools.DB import DAL
import numpy as np

def select_pacs_exam_path_per_id(patient_id):
    """
    医院pacs:获取指定pid 影像
    :param patient_id: 影像号
    :return: path 影像路径

    """ 
    #orc = DAL.Oracle(user, pwd, ip, port, database)
    #sql = ""
    #rowcount,result = orc.execute(sql)
    #orc.close()
    #return result

def select_id_list_from_study_status(TEST):
    """
    医院ris:获取已检查但医生未写报告的病人
    :return: patient 病人基本信息 type list
    """
    if TEST:
        return [[str(i), ""] for i in np.random.randint(10000000, 99999999, 10)]
    #orc = DAL.Oracle(user, pwd, ip, port, database)
    #sql = ""
    #rowcount,result = orc.execute(sql)
    #orc.close()
    #return result


def insert_patient_information(patient):
    """
    推想DB:插入病人基本信息
    :param patient: 病人信息
    :return: rowcount 受影响行数
    """
    #orc = DAL.Oracle(user, pwd, ip, port, database)
    #sql = ""
    #rowcount,result = orc.execute(sql)
    #orc.close()
    #return boolean

def select_history_information(patient,TEST):
    """
    推想DB:查询当前病人历史信息
    :param patient:病人信息
    :return: patient_history 病人历史信息 list
    """
    if TEST:
        return [[patient[0] + "1", ""], [patient[0] + "2", ""], [patient[0] + "3", ""]]
    #msql = DAL.Mysql(ip='127.0.0.1', port='3306', user='txkj', pwd='txkj', database='txdata')
    #sql = ""
    #rowcount,result = msql.execute(sql)
    #orc.close()
    #return result


def update_patient_predict_information(predict):
    """
    推想DB:更新病人预测信息
    :param predict: 预测结果
    :return: rowcount 受影响行数
    """
    #msql = DAL.Mysql(ip='127.0.0.1', port='3306', user='txkj', pwd='txkj', database='txdata')
    #sql = ""
    #rowcount,result = msql.execute(sql)
    #orc.close()
    #return rowcount

def select_patient_rows(patient_id):
    """
    推想DB:验证数据是否存在当前病人
    :param patient_id: 影像号
    :return: rowcount 受影响行数
    """
    #msql = DAL.Mysql(ip='127.0.0.1', port='3306', user='txkj', pwd='txkj', database='txdata')
    #sql = ""
    #rowcount,result = msql.execute(sql)
    #orc.close()
    #return rowcount
