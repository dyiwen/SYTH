# -*- coding: utf-8 -*-

import sys, os

class FTPrsync(object):
    """
    FTP 远程同步到本地
    """
    def __init__(self, debug = 0):
        from ftplib import FTP, error_perm
        self.ftp = FTP()
        self.error_perm = error_perm 
        self.bufsize = 1024   
        self.ftp.set_debuglevel(debug)
        print 'ftp sync init'

    def out(self, x):
        print x
        
    def Connection(self, host='127.0.0.1', port=21, timeout=60):
        """
        function:连接FTP
        """
        self.ftp.connect(host, port, timeout) # 连接FTP
        
    def Login(self, user='', pwd= ''):
        """
        function:登陆FTP账户
        """
        self.ftp.login(user,pwd) # 登录 
    
    
    def mkdirs(self, folder):
        """
        function:创建目录
        """
        try:
            if not os.path.isdir(folder):
                os.makedirs(folder)
                self.out("Created directory: " + folder)
        except OSError:
            print "Created directory failed to "+ folder
    
    def uploadFile(self, ftp, remotepath, localpath):
        self.ftp.storbinary('STOR '+ remotepath , open(localpath,"rb"), self.bufsize) #上传文件
        self.ftp.set_debuglevel(self.debug)
        self.out("upload: " + remotepath)
        
    def downloadFile(self, remotepath, localpath):
        """
        function:下载ftp指定文件保存成指定文件
        params: remotepath >> 下载ftp的文件路径
                localpath >> 保存本地的文件路径
        """
        self.ftp.retrbinary("RETR " + remotepath, open(localpath,"wb").write, self.bufsize)
        
        self.out("downloaded: " + remotepath)
        
    def traverse_DownloadFile(self, tree = True):
        """
        function:遍历当前目录,下载所有文件并保留目录结构     
        params: tree >> True 保留原始分支结构
                tree >> False 非
        """
        fileList = self.ftp.nlst()
        for fileName in fileList:
            try:
                self.ftp.cwd(fileName)       
                if tree:
                    self.mkdirs(fileName)
                    os.chdir(fileName) #设置本地路径
                self.traverse_DownloadFile(tree)      
            except self.error_perm:
                try:
                    self.downloadFile(fileName,fileName)
                except:
                    print("Error: File could not be downloaded " + fileName)
        try:
            self.ftp.cwd('../')
            if tree:
                os.chdir('../')
        except:
            print("Error: could not change to ../")
    
   
    def sync(self, source, destination, tree = False):
        """
        function:同步ftp目录到本地目录
        params：source >> ftp目录
                destination >> 本地存放目录
                tree >> True 保留原始分支结构
        """ 
        try:
            self.ftp.cwd(source) # 设置FTP路径
            fileList = self.ftp.nlst()
            if len(fileList) >= 70 and len(fileList) <= 999:
                self.mkdirs(destination) #创建本地目录
                os.chdir(destination) #设置本地路径
                self.traverse_DownloadFile(tree)
        except OSError:     
            print "Error: could not change the local path to " + destination
        except self.error_perm:       
            print "Error: could not change to " + source
            #sys.exit("Ending Application")
        finally:
            self.ftp.quit()
        
                
class RsyncExtra(FTPrsync):
    """
    继承FTPSync
    """
    def __init__(self, user='ftp', pwd= 'ftp', host='127.0.0.1', port=21, timeout=60, debug=1):
        super(RsyncExtra, self).__init__(debug)
        self.Connection(host, port, timeout)
        self.Login(user, pwd)
            
    def func(self, x):
        """
        function:自定义方法,[params] X >> 获取的文件名
        """
        print x    
        
    def downloadFile(self, remotepath, localpath):
        """
        function:下载ftp指定文件保存成指定文件
        params: remotepath >> 下载ftp的文件路径
                localpath >> 保存本地的文件路径
        """
        self.ftp.retrbinary("RETR " + remotepath, open(localpath,"wb").write, self.bufsize)
        self.out("downloaded: " + remotepath)
        self.func(localpath)
    
    """ 完善中
    def show(self, list):
        result = list.lower().split( " " )
        if self.path in result and "<dir>" in result:
            self.bIsDir = True
     
    def isDir(self, path):
        self.bIsDir = False
        self.path = path
        #this ues callback function ,that will change bIsDir value
        self.ftp.retrlines( 'LIST', self.show )
        return self.bIsDir
    """
    
if __name__ == "__main__":
    ftpsync = RsyncExtra()
    #ftpsync.out = lambda x:x
    ftpsync.func = lambda x:x
    ftpsync.sync('1/','/tmp/test/123/',tree = False) #非结构化 同步远程目录1/到本地目录/tmp/test/123/
    
