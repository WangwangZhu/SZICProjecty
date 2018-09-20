#! /usr/bin/env python3
###############################################################################################################
###############################################################################################################
# 文件名称：
# 文件功能：
# 备注信息：
##############################################################################################################
##############################################################################################################

import sys 
sys.path.append('/usr/local/lib/python3.5/dist-packages/')
from canlib import kvadblib
from canlib import Frame
import canlib.canlib as canlib 
import numpy as np 
import time
###############################################################################################################
# 函数名称：setUpChannel()
# 函数功能：打开CAN通道，设置CAN通信的波特率并且启动通道
# 输入参数：
# 返回值  ：返回的内容用于供关闭通道的函数调用
# 备注信息：
##############################################################################################################
def setUpChannel(channel=0,openFlags=canlib.canOPEN_ACCEPT_VIRTUAL,
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
# 函数名称：tearDownChannel()
# 函数功能：失能并关闭通
# 输入参数：
# 返回值  ：返回的内容用于供关闭通道的函数调用
# 备注信息：
##############################################################################################################
def tearDownChannel(ch):
    ch.busOff()
    ch.close()



###############################################################################################################
# 程序执行主体
##############################################################################################################
ch0 = setUpChannel(channel=0)
#print('canlib version',canlib.canlib.getVersion(ch0))
frame = Frame(id_=0x00000112,data=[1,222,00],flags = canlib.canMSG_STD)
id_ = 0x00000112 
data=bytearray(b'\x01\x01\xB4\x00\x00\x00\x00\x00')

while True:
    ch0.write(frame)
    print('持续发送中')
    time.sleep(1)
#ch0.write(id_,data,canlib.canMSG_STD)
print('发送完成')
#while True:
#    id_,msg,dlc,flag,time = ch0.read(timeout = -1)
##    print('收到数据：')
#    print(id_)
#    print(msg)
#    print(dlc)
#    print(flag)
#    print(time)

tearDownChannel(ch0)












