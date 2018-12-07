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
from multiprocessing import Process,Queue,Lock 

###############################################################################################################
# 函数名称：openChannel()
# 函数功能：打开CAN通道，设置CAN通信的波特率并且启动通道
# 输入参数：
# 返回值  ：返回的内容用于供关闭通道的函数调用,并且用于发送函数与接受函数的通道选择
# 备注信息：
##############################################################################################################
def openChannel(channel=0,openFlags=canlib.canOPEN_ACCEPT_VIRTUAL,bitrate=canlib.canBITRATE_500K,bitrateFlags=canlib.canDRIVER_NORMAL):
    #  cl = canlib.canlib()
    ch = canlib.openChannel(channel,openFlags)
    num_channels = canlib.getNumberOfChannels()
    print("num_channels:%d"%num_channels)
    print("%d. %s (%s / %s)" % (num_channels, canlib.ChannelData(0).channel_name,
        canlib.ChannelData(0).card_upc_no,canlib.ChannelData(0).card_serial_no)) 
    ch.setBusOutputControl(bitrateFlags)
    ch.setBusParams(bitrate)
    ch.busOn()
    #  print("somethin wrong***************************************")
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
# 函数名称：ReveiveCan()
# 函数功能：接受CAN总线网络数据
# 输入参数：
# 返回值  ：
# 备注信息：根据DBC筛选接受到的数据
##############################################################################################################
def ReceiveCan(qCANDataReceive,ch0,qCANDataReceiveLock):

    db = kvadblib.Dbc(filename = r'../CAN/ClubCar_V3_withoutME.dbc')

    EPSFeedback = db.get_message_by_name('EPSSteeringAngleFeedback')
    #  EBSFeedback = db.get_message_by_name('E')
    #  EPSFeedback = EPSFeedback.bind()
    #  EPS_02Feedback = db.get_message_by_name('EPS_02')
    print('***************************8')
    while True:
        EPSFeedbackMsg = ch0.read(timeout = 1000)
        if EPSFeedbackMsg.id == 485:
            #  bmsg = db.interpret(EPSFeedbackMsg)
            #  msg = bmsg._message
            #  EPS_02FeedbackMsg = EPS_02Feedback.bind(ch0.read(timeout = 100))
            #  print("方向盘转角反馈：%s" % msg.name)
            EPSFeedbackMsg = EPSFeedback.bind(EPSFeedbackMsg)
            #  print("方向盘转角反馈：%s" % EPSFeedbackMsg.EPS_SteeringAngle.phys)
            with qCANDataReceiveLock:
                if qCANDataReceive.empty():
                    #  print(33333333333333333333)
                    qCANDataReceive.put(['EPSFeedBackAngle',EPSFeedbackMsg.EPS_SteeringAngle.phys])
                    #  print(11111111111111111111111)
                else:
                    #  print(44444444444444444444444444)
                    while not qCANDataReceive.empty():
                        #  print(555555555555555555)
                        qCANDataReceive.get(True)
                        #  print(222222222222222222222)
                #  print(EPSFeedbackMsg)
        time.sleep(0.001)

        

###############################################################################################################
# 函数名称：SendCan(qCANDATA,q)
# 函数功能：更新CAN总线数据并且将三个线控控制量发送到总线上
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
def SendCan(qCANDataSend,ch0):

    db = kvadblib.Dbc(filename = r'../CAN/ClubCar_V3_withoutME.dbc') # 打开DBC库文件 

    EPSEnableStatus = 0    
    EPSInputValue = 0
    ThrottleValue = 0
    EBSEnableStatus= 0
    EBSInputValue= 1

    lock = threading.Lock()
    def CANDataUpdate():
        nonlocal EPSEnableStatus 
        nonlocal EPSInputValue 
        nonlocal ThrottleValue 
        nonlocal EBSEnableStatus 
        nonlocal EBSInputValue 
        while True:
            lock.acquire()
            try:
                dataReceive = qCANDataSend.get(True)

                if dataReceive[0] == 'EPSInputEnable':
                    EPSEnableStatus = dataReceive[1]

                if dataReceive[0] == 'EPSInput':
                    EPSInputValue= dataReceive[1] 

                if dataReceive[0] == 'ThrottleInput':
                    ThrottleValue= dataReceive[1] 

                if dataReceive[0] == 'EBSInputEnable':
                    EBSEnableStatus = dataReceive[1] 

                if dataReceive[0] == 'EBSInput':
                    EBSInputValue = dataReceive[1] 
            finally:
               lock.release()
            time.sleep(0.01)

    def CANSendMessage():
        nonlocal EPSEnableStatus 
        nonlocal EPSInputValue 
        nonlocal ThrottleValue 
        nonlocal EBSEnableStatus 
        nonlocal EBSInputValue 
        while True:
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
            EBSInput.EBS_brakePadel.phys = EBSInputValue 
            
            ch0.write(EPSInput._frame)
            ch0.write(ThrottleInput._frame)
            ch0.write(EBSInput._frame)
            #  print(EPSInput)
            time.sleep(1/50.0) # 50为CAN总线网络控制量的刷新率
            #  print('发送完成')
    t1 = threading.Thread(target = CANDataUpdate)
    t2 = threading.Thread(target = CANSendMessage)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


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

    qCANDataReceiveLock = Lock()

    qCANDataReceive = Queue(maxsize = 1000)
    qCANDataSend = Queue()

    ch0 = openChannel(0)

    processCANSendMsg = Process(target=SendCan,args = (qCANDataSend,ch0))
    processCANSendMsg.start()
    
    processCANReceive = Process(target=ReceiveCan,args = (qCANDataReceive,ch0,qCANDataReceiveLock))
    processCANReceive.start()

    # 模拟MPC计算出的数据
    a = 1
    b = 0
    while True:
        qCANDataSend.put(['EPSInputEnable',0])
        qCANDataSend.put(['EPSInput',0])

        qCANDataSend.put(['ThrottleInput',0])

        qCANDataSend.put(['EBSInputEnable',1])
        qCANDataSend.put(['EBSInput',0])
        with qCANDataReceiveLock:
            if not qCANDataReceive.empty():
                #  print("队列长度",qCANDataReceive.qsize())
                EPSFeedbackAnglePhys = qCANDataReceive.get(True)
                if EPSFeedbackAnglePhys[0] == 'EPSFeedBackAngle':
                    print("方向盘转角反馈：%s" % EPSFeedbackAnglePhys[1])

        #  print("Reveiveing from : %s" % str(ch0.read()))
        #  data = qCANDATA.get(True)
        #print(qCANDATA.get(True)[1])
        #print(qCANDATA.get(True)[0])
        #  print(data)
        time.sleep(0.02)
































   #   qCANDATA.put(0)
    #  qCANDATA.put(9)
    #  qCANDATA.put(34)
    #  qCANDATA.put(0)
    #  qCANDATA.put(0)
    #  qCANDATA.put(0)
    #  qCANDATA.put(0)
    #  qCANDATA.put(0)
    #  qCANDATA.put(0)













#      t1 = threading.Thread(target=KeyInternal)
    #  t2 = threading.Thread(target=SenInternal,args=(EPSInput,))
    #  t3 = threading.Thread(target=CANDdataReceive,)
    #  t1.start()
    #  t2.start()
    #  t3.start()
    #  t1.join()
    #  t2.join()
    #  t3.join()




    # while True:dd

        #  value.append(qCANDATA.get(True)) # python 里面的.get 是阻塞式接受。

        #  lock.acquire()
        #  try:
        #      EPSInputValue = value[0]
        #      EPSEnableStatus = value[1]
        #      ThrottleValue = value[2]
        #      EBSInputValue = value[3]
        #      EBSEnableStatus = value[4]
        #
        #  finally:<F5>
            #  lock.release()

#          EPSInput.SteeringAngleRequest.phys = EPSInputValue # 根据传入进程的数据更新参数
        #  EPSInput.EPSMode.phys = EPSEnableStatus
        #
        #  ThrottleInput.throttle.phys = ThrottleValue
        #
        #  EBSInput.EBS_brakeEnable.phys = EBSEnableStatus
        #  EBSInput.EBS_brakePadel.phys = EBSInputValue
#
   #          print(EPSInputValue)
        #  print(ThrottleValue)
        #  print(EBSInputValue)
        #  time.sleep(0.02)



###############################################################################################################
# 函数名称：
# 函数功能：
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################

#      #  def KeyInternal():
        #  nonlocal EPSEnableStatus
        #  nonlocal EBSEnableStatus
        #  while True:
        #      EPSEnableStatus = q.get(True)
        #      EBSEnableStatus = EPSEnableStatus
            #print('状态发生改变了')
            #print(EPSEnableStatus) 
     
#      def CANDdataReceive():
        #  nonlocal EPSInputValue
        #  nonlocal ThrottleValue
        #  nonlocal EBSInputValue
        #  value = []
        #  i = 0
        #  while True:
        #      value.append(qCANDATA.get(True))
        #      i = i+1
        #      if i == 3:
        #          i = 0
        #          lock.acquire()
        #          try:
        #              EPSInputValue = value[0]
        #              ThrottleValue = value[1]
        #              EBSInputValue = value[2]
        #              #print('value',value)
        #              #print(EPSInputValue)
        #              #print(ThrottleValue)
        #              #print(EBSInputValue)
        #          finally:
                    #  lock.release()
#      def SenInternal(EPSInput):
        #  nonlocal EPSEnableStatus
        #  nonlocal EBSEnableStatus
        #  nonlocal EPSInputValue
        #  nonlocal ThrottleValue
        #  nonlocal EBSInputValue
#  #    parser = argparse.ArgumentParser(description = 'Create a database from scratch.')
#    parser.add_argument('filename',help=('The filename to save to the database to.'))
#    parser.add_argument('-n','--name',default='Engine example',help=('The name of the database(not filename, the internal name)'))
#    args = parser.parse_args()
#
#    createDatabase(args.name,args.filename)
