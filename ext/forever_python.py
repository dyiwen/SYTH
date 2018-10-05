# -*- coding: utf-8 -*-


import os, time

"""
function:创建日志
reutrn logging object
"""
def create_logging(filepath='info.log',mode = 'a'):
    import logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=filepath,
                        filemode= mode)
    return logging

"""
守护python 进程
"""
def forever_python(search_cmd_list, start_cmd_list, true_name):
    while True:
        for i, cmd in enumerate(search_cmd_list):
            time.sleep(10)
            result = os.popen(cmd).read()
            if true_name[i] not in result:
                os.system(start_cmd_list[i])
                logging.info(start_cmd_list[i])
                
if __name__ == "__main__":
    
    search_cmd_list = [
    #"ps -ef| frep ./main.js",
    #"ps -ef| grep ./imageServer.js",
    #"ps -ef| grep ./server.py",
    "ps -ef | grep ./multi_server.py",
    "ps -ef| grep ./upload.js",
    "ps -ef| grep ./download.js",
    #"ps -ef | grep './dlserver.py 0 0'",
    #"ps -ef | grep './dlserver.py 1 1'",
    #"ps -ef | grep './dlserver.py 2 2'",
    #"ps -ef | grep './dlserver.py 3 3'"
    ]
    
    start_cmd_list = [
    #"cd /home/tx-deepocean/Infervision/OHIF/tx_ohif_viewer/ &&( MONGO_URL=mongodb://localhost:27017/test ROOT_URL=http://127.0.0.1 PORT=3000 node ./main.js &)",
    #"cd /home/tx-deepocean/Infervision/tx_ct_view/ && (node ./imageServer.js &)",
    #"cd /home/tx-deepocean/Infervision/tx_pacs_scp/ && (python ./server.py &)",
    "cd /home/tx-deepocean/Infervision/tx_hospital_interface/ && (python ./multi_server.py &)",
    "cd /home/tx-deepocean/Infervision/tx_file_upload/ && (node ./upload.js &)",
    "cd /home/tx-deepocean/Infervision/tx_file_download/ && (node ./download.js &)",
    #"cd /home/tx-deepocean/Infervision/tx_dlserver/ && (python ./dlserver.py 0 0 &)",
    #"cd /home/tx-deepocean/Infervision/tx_dlserver/ && (python ./dlserver.py 1 1 &)",
    #"cd /home/tx-deepocean/Infervision/tx_dlserver/ && (python ./dlserver.py 2 2 &)",
    #"cd /home/tx-deepocean/Infervision/tx_dlserver/ && (python ./dlserver.py 3 3 &)"
    ]       
    
    true_name = [
    #"node ./main.js",
    #"node ./imageServer.js",
    #"python ./server.py",
    "python ./multi_server.py",
    "node ./upload.js",
    "node ./download.js",
    #"python ./dlserver.py 0 0",
    #"python ./dlserver.py 1 1",
    #"python ./dlserver.py 2 2",
    #"python ./dlserver.py 3 3"
    ]

    logging = create_logging(".forever_python.log")
    forever_python(search_cmd_list, start_cmd_list, true_name)
