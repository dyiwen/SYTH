# coding=utf-8
'''
Data Access Layer
@author: dyiwen
'''
import pymssql,ibm_db

class sqlserver(object):

    def __init__(self, host, user, pwd,):
        # connstr = "host={},user={},password={},charset=utf8".format(host,user,pwd)
        self._conn = pymssql.connect(host='{}'.format(host),user='{}'.format(user),password='{}'.format(pwd),charset='utf8')
        self._cursor = self._conn.cursor()

    def execute(self, sql):
        self._cursor.execute(sql)
        return self._cursor.rowcount, self._cursor.fetchall()

    def close(self):
        self._cursor.close()
        self._conn.close()

class DB2(object):
    
    def __init__(self, db, host, port, user, pwd):
        connstr = "DATABASE={};HOSTNAME={};PORT={};PROTOCOL=TCPIP;UID={};PWD={};".format(db,host,port,user,pwd)
        self._conn = ibm_db.connect(connstr,"","")

    def execute(self,sql):
        self._stmt = ibm_db.exec_immediate(self._conn,sql)
        self._result = ibm_db.fetch_tuple(self._stmt)
        self.result_list = []
        while(self._result):
            self.result_list.append(self._result)
            self._result = ibm_db.fetch_tuple(self._stmt)
        return self.result_list

    def close(self):
        ibm_db.close(self._conn)
