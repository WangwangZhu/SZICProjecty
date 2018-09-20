#! /usr/bin/env python3
#coding=utf-8
###############################################################################################################
###############################################################################################################
# 文件名称：maniFunction.py
# 文件功能：用于协调各个模块的运行
# 备注信息：
##############################################################################################################
##############################################################################################################
import sys 
from multiprocessing import Process,Queue 
sys.path.append(r'../CAN')
sys.path.append(r'../INS')
sys.path.append(r'../MPC')
sys.path.append(r'../KeyBoardMonitor')
sys.path.append(r'../Cameras')
sys.path.append(r'../Lidar')
import time 
import sendReceiveByDbc
import INSDataCollection
import MPCTracking 
import keyBoardMonitor
###############################################################################################################
# 程序执行主体
##############################################################################################################

###############################################################################################################
# 函数名称：__main__()
# 函数功能：主调函数
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
if __name__ == '__main__':
    #t1 = threading.Thread(target=SendCan(),name='SendCan')
    #t2 = threading.Thread(target=InputKey(),name='InputKey')
    #t1.start()
    #t2.start()
    qKeyBoardEPSEBSEnable = Queue()
    qCANDATA = Queue()
    qINSDATA = Queue()
    p1 = Process(target=sendReceiveByDbc.SendCan,args = (qCANDATA,qKeyBoardEPSEBSEnable))
    p2 = Process(target=keyBoardMonitor.InputKey,args=(qKeyBoardEPSEBSEnable,))
    p3 = Process(target=INSDataCollection.INSDataGet,args=(qINSDATA,))
    p4 = Process(target=MPCTracking.MPCTrackingControler,args=(qINSDATA,))
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    qCANDATA.put(0)
    qCANDATA.put(0)
    qCANDATA.put(00)
    time.sleep(1000)
#    parser = argparse.ArgumentParser(description = 'Create a database from scratch.')
#    parser.add_argument('filename',help=('The filename to save to the database to.'))
#    parser.add_argument('-n','--name',default='Engine example',help=('The name of the database(not filename, the internal name)'))
#    args = parser.parse_args()
#
#    createDatabase(args.name,args.filename)





















###############################################################################################################
# 函数名称：
# 函数功能：
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################


