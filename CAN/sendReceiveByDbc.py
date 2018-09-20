#! /usr/bin/env python3
###############################################################################################################
###############################################################################################################
# 文件名称：sendReceiveByDbc.py
# 文件功能：用于通过DBC文件实现CAN总线数据的收发
# 备注信息：
##############################################################################################################
##############################################################################################################

from __future__ import print_function
import sys 
sys.path.append('/usr/local/lib/python3.5/dist-packages/')
from canlib import kvadblib
from canlib import Frame
from canlib import canlib 
import time
import argparse
from collections import namedtuple
import textwrap
import threading
import sys
import tty
import termios
import os
import pyxhook
from multiprocessing import Process,Queue 

###############################################################################################################
# 函数名称：openChannel()
# 函数功能：打开CAN通道，设置CAN通信的波特率并且启动通道
# 输入参数：
# 返回值  ：返回的内容用于供关闭通道的函数调用
# 备注信息：
##############################################################################################################
def openChannel(
        channel=0,
        openFlags=canlib.canOPEN_ACCEPT_VIRTUAL,
        bitrate=canlib.canBITRATE_500K,
        bitrateFlags=canlib.canDRIVER_NORMAL):
    cl = canlib.canlib()
    ch = cl.openChannel(channel,openFlags)
    print('Using channel: %s, EAN: %s'%(ch.getChannelData_Name(),ch.getChannelData_EAN()))
    ch.setBusOutputControl(bitrateFlags)
    ch.setBusParams(bitrate)
    ch.busOn()
    return ch

###############################################################################################################
# 函数名称：closeChannel()
# 函数功能：失能并关闭通
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
def closeChannel(ch):
    ch.busOff()
    ch.close()

###############################################################################################################
# 函数名称：closeChannel()
# 函数功能：失能并关闭通
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
def SendCan(qCANDATA,q):
    lock = threading.Lock()

    EPSEnableStatus = 1
    EPSInputValue = 0 
    ThrottleValue = 0 
    EBSEnableStatus=1
    EBSInputValue=0  
    
    db = kvadblib.Dbc(filename=r'../CAN/ClubCar_V3_withoutME.dbc') # 打开DBC库文件
    EPSInput = db.get_message_by_name('EPSInput') # 根据帧的名字获取帧
    EPSInput = EPSInput.bind() # 生成一个捆绑报文
    EPSInput.EPSMode.phys = EPSEnableStatus 
    EPSInput.SteeringAngleRequest.phys = EPSInputValue 
    ThrottleInput = db.get_message_by_name('throttleInput')
    ThrottleInput = ThrottleInput.bind()
    ThrottleInput.throttle.phys = ThrottleValue 
    EBSInput = db.get_message_by_name('EBS')
    EBSInput = EBSInput.bind()
    EBSInput.EBS_brakeEnable.phys = EBSEnableStatus
    EBSInput.EBS_brakePadel.phs = EBSInputValue 
    
    ch0 = openChannel(0)
    def KeyInternal():
        nonlocal EPSEnableStatus
        nonlocal EBSEnableStatus 
        while True:
            EPSEnableStatus = q.get(True)
            EBSEnableStatus = EPSEnableStatus 
            #print('状态发生改变了')
            #print(EPSEnableStatus) 
     
    def CANDdataReceive():
        nonlocal EPSInputValue
        nonlocal ThrottleValue 
        nonlocal EBSInputValue
        value = []
        i = 0
        while True:
            value.append(qCANDATA.get(True))
            i = i+1
            if i == 3:
                i = 0
                lock.acquire()
                try:
                    EPSInputValue = value[0]
                    ThrottleValue = value[1]
                    EBSInputValue = value[2]
                    #print('value',value)
                    #print(EPSInputValue)
                    #print(ThrottleValue)
                    #print(EBSInputValue)
                finally:
                    lock.release()
    def SenInternal(EPSInput):
        nonlocal EPSEnableStatus
        nonlocal EBSEnableStatus
        nonlocal EPSInputValue
        nonlocal ThrottleValue 
        nonlocal EBSInputValue 

        while True:
            EPSInput.SteeringAngleRequest.phys = EPSInputValue 
            EPSInput.EPSMode.phys = EPSEnableStatus 
            ThrottleInput.throttle.phys = ThrottleValue
            EBSInput.EBS_brakeEnable.phys = EBSEnableStatus
            EBSInput.EBS_brakePadel.phys = EBSInputValue 
            #print('SenInternal',EPSEnableStatus)
            #print(EPSInputValue)
            #print(ThrottleValue)
            #print(EBSInputValue)
            ch0.write(EPSInput._frame)
            ch0.write(ThrottleInput._frame)
            ch0.write(EBSInput._frame)
            print('发送完成')
            time.sleep(0.02)
    t1 = threading.Thread(target=KeyInternal)
    t2 = threading.Thread(target=SenInternal,args=(EPSInput,))
    t3 = threading.Thread(target=CANDdataReceive,)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
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
    q = Queue()
    qCANDATA = Queue()
    p1 = Process(target=SendCan,args = (qCANDATA,q,))
    p2 = Process(target=InputKey,args=(q,))
    p1.start()
    p2.start()
    #q.put(2)
    qCANDATA.put(9)
    qCANDATA.put(9)
    qCANDATA.put(34)
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
