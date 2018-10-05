智能辅助阅片-接口（对接医院）
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


常修改地方（注意地方）
* multi_server.py  
    * function: service()
        * 选择合适获取DICOM文件的方式 或 本地编写function；
        * file_number 设置预测最小文件个数；
        * Dicomfilter().CT() 根据实际情况编写过滤条件
    * function: main() 
        * 可选择开启历史前后片对比功能，history_patient_list[:] 默认获取所有历史，若只想获取最新一条检查 history_patient_list[:1] 
    * function: Multi() 
        * cpuCount= 改成4或者6，默认是CPU支持的最大进程数       
    * channelCount 对应多通道的DLSERVER
    
* sqlserver.py 根据医院数据库结构本地编写SQL     
* server.conf  server_sleep 为每轮之间暂停的时间，可根据实际需要修改，建议15-60之间    
* constants.py  取消注释out函数中的print用于观察     
 


