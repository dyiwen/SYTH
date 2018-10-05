dicom数据拉取清洗发送接口
===
 * tools/ 工具集合
 * reset.py 重置/生成配置文件（./server.conf）
 * server.py 服务启动 
 * constants.py 公共常量
 * sqlserver.py sql管理
 * pulldata.py 获取DICOM
 * ext/ 附加的功能


* 重置/生成配置文件

```
$ python reset.py
```
* 启动

```
$ python multi_server.py
```     

* 测试   
默认会执行多轮测试，输出的每一轮运行时间等于30/cpuCount*10则多进程没有问题    
测试无误后需要修改：    
    TEST=True改为False    

（注意地方）
* DAL.py 针对性封装类sqlserver和db2两个库，由sql_test.py调用
    * sql_test.py 查询两库视图，数据清洗后返回

* multi_server.py  
    * function: service()
        * 调用pulldata选择合适拉取方式（ftp/磁盘挂载/gdcm/wget/scp） 或 本地编写function；
        * file_number 返回拉取后的文件数量
    * function: main() 
        * 数据清洗函数 
    * function: Multi() 
        * 分配进程
        * cpuCount= 改成4或者6，默认根据CPU核数CPUCOUNT()分配最大进程数，一般为12       
    * channelCount 对应多通道的REDIS的预测频道

* pulldata.py 数据拉取过滤清洗等处理主函数，该项目由FTP拉去更改自磁盘挂载，进行拉取-解压图像-清洗-改名-脱敏-格式化保存等操作
* server.conf  常用参数配置文件，server_sleep 为每轮之间暂停的时间，可根据实际需要修改，建议15-60之间    
* constants.py  相关日志配置信息，out,err,warn根据日志等级分别封装，取消注释out函数中的print用于观察     
 
* /log/ 主日志目录

