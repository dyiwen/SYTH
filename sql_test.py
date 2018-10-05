#!/usr/bin/env python
# encoding: utf-8
import DAL
import json, os

def show_china(s):
	print json.dumps(s, indent = 0,ensure_ascii = False)

#----------------------------------------------------------------------------------------------------
def select_pacs_exam_path_per_id(patient_id):
	pass

def select_id_list_from_sqls(TEST):
	con_sqls = DAL.sqlserver('192.168.130.113','txkj','txkj')
	sql = "select RIS_ID,CheckPart,CONVERT(varchar(100),EXAM_DATE,112) from v_TX_PACS where EXAM_DATE >= convert(varchar(8),getdate(),112) and (CheckPart like '%上腹%' or CheckPart like '%胸%' or CheckPart like '%全腹%') "
	rowcount, result = con_sqls.execute(sql)
	con_sqls.close()
	#Ris_list = [i[0] for i in result]
	Ris_list = []
	for i in result:
		if len(str(i[0])) == 7 and '0'+str(i[0]) not in Ris_list:
			Ris_list.append('0'+str(i[0]))
		elif len(str(i[0])) == 8 and str(i[0]) not in Ris_list:
			Ris_list.append(str(i[0]))
	#print Ris_list, '------'+str(len(Ris_list))
	return Ris_list

def select_path_from_db2(ris_list):
	con_db2 = DAL.DB2('IPACSDB','192.168.130.66','50000','db2inst1','db2inst1')
	if con_db2:
		Ris_list = ris_list
		Patient_info_list = []
		for ris_id in Ris_list:
			sql = "select PATIENT_ID,SERIES_UID,to_char(STUDY_DATE,'yyyymmdd') from PACS.TX_PACS where PATIENT_ID = '{}' and to_char(STUDY_DATE,'yyyy-mm-dd') >= CURRENT DATE".format(ris_id)
			result = con_db2.execute(sql)
			if len(result) > 0:
				root = '/media/tx-deepocean/Data/isilon.thyy.com/'
				series_list = [root+s[2]+'/CT/'+s[1] for s in result]
				patient_info = [s[0],series_list]
				Patient_info_list.append(patient_info)
	#print Patient_info_list,'---------'+str(len(Patient_info_list))		
	print Patient_info_list
	con_db2.close()
	return Patient_info_list
#------------------------------------------------------------------------------------------------------------------------------------------------------------

def sql_t():
	con_db2 = DAL.DB2('IPACSDB','192.168.130.66','50000','db2inst1','db2inst1')
	if con_db2:
		sql = "select PATIENT_ID,SERIES_UID,to_char(STUDY_DATE,'yyyymmdd') from PACS.TX_PACS where PATIENT_ID = '{}' and to_char(STUDY_DATE,'yyyy-mm-dd') >= CURRENT DATE".format('79006304')
		result = con_db2.execute(sql)
		print result
		Patient_info_list = []
		if len(result) > 0:
			root = '/media/tx-deepocean/Data/isilon.thyy.com/'
			series_list = [root+s[2]+'/CT/'+s[1] for s in result]
			patient_info = [s[0],series_list]
			Patient_info_list.append(patient_info)
	
	print Patient_info_list[0][0],Patient_info_list[0][1],'---------'+str(len(Patient_info_list))		
	#print result
	con_db2.close()
	return Patient_info_list

def sql_txt(patient_id):
	con_sqls = DAL.sqlserver('192.168.130.113','txkj','txkj')
	#sql = "select RIS_ID,CheckPart,REP_DESC,REP_RESULT,CONVERT(varchar(100),EXAM_DATE,112) from v_TX_PACS where EXAM_DATE >= convert(varchar(8),getdate(),112) and (CheckPart like '%上腹%' or CheckPart like '%胸%' or CheckPart like '%全腹%') and RIS_ID = {}".format(patient_id)
	sql = "select RIS_ID,CheckPart,REP_DESC,REP_RESULT,CONVERT(varchar(100),EXAM_DATE,112) from v_TX_PACS where EXAM_DATE >= convert(varchar(8),getdate(),112) and RIS_ID = '{}'".format(patient_id)
	rowcount, result = con_sqls.execute(sql)
	con_sqls.close()
	print show_china(result)
	#print result
	# a = []
	# for i in result:
	# 	if len(i[3]) != 0 and len(i[4]) !=0:
	# 		a.append(i)
	# print a
	# print len(a)



	# #Ris_list = [i[0] for i in result]
	# Ris_list = []
	# for i in result:
	# 	if len(str(i[0])) == 7 and '0'+str(i[0]) not in Ris_list:
	# 		Ris_list.append('0'+str(i[0]))
	# 	elif len(str(i[0])) == 8 and str(i[0]) not in Ris_list:
	# 		Ris_list.append(str(i[0]))
	# #print Ris_list, '------'+str(len(Ris_list))
	#return Ris_list
	return result


def get_txt():
	root = '/media/tx-deepocean/Data/DICOMS/test'
	patient_id_list = os.listdir(root)[:104]
	print patient_id_list
	print len(patient_id_list)
	a = []
	for patient_id in patient_id_list:
		result = sql_txt(patient_id)
		# print result
		# print result[0][3]
		# break
		try:
			if result[0][3] != None and result[0][4] != None:
				a.append(result)
		except:
			print 'Error'
	# print a
	# print len(a) 
	for v in a:
		print v
		print v[0][0]
		print str(v[0][2].encode('utf8'))
		print str(v[0][3].encode('utf8'))
		with open('/media/tx-deepocean/Data/DICOMS/report','a') as f:
			f.write(str(v[0][0])+'\n')
			f.write(str(v[0][2].encode('utf8'))+'\n')
			f.write(str(v[0][3].encode('utf8'))+'\n')
			f.write('-'*40+'\n')




if __name__ == '__main__':
	#select_id_list_from_sqls(False)
	#select_path_from_db2(select_id_list_from_sqls(False))
	#sql_t()
	sql_txt('79006304')
	#get_txt()

