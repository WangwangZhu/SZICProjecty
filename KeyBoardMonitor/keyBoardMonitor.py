#! /usr/bin/env python3
###############################################################################################################
###############################################################################################################
# 文件名称：keyBoardMonitor.py
# 文件功能：用于键盘输入监控，由众多的状态机写成
# 备注信息：
##############################################################################################################
##############################################################################################################

from __future__ import print_function
import sys 
sys.path.append('/usr/local/lib/python3.5/dist-packages/')
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
# 函数名称：InputKey
# 函数功能：监控键盘输入
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
def InputKey(qKeyBoardEPSEBSEnable):
    #global EPSEnableStatus
    def kbenent(event):
        global running 
        if event.Key == 'q' or event.Key == 'qq':
            print('wo chengongle')
            qKeyBoardEPSEBSEnable.put(0)
        if event.Key == 'e' or event.Key == 'ee':
            qKeyBoardEPSEBSEnable.put(1)
            #EPSEnableStatus = 0
        if event.Ascii == 32:
            running = False
    hookman = pyxhook.HookManager()
    hookman.KeyDown = kbenent 
    hookman.start()
    running = True
    while running :
        time.sleep(0.1)
    hookman.cancel()
##    while True:
#        fd = sys.stdin.fileno()
#        old_settings = termios.tcgetattr(fd)
#        try:
#            tty.setraw(fd)
#            ch = sys.stdin.read(1)
#        finally:
#            termios.tcsetattr(fd,termios.TCSADRAIN,old_settings)
#        print('ch',ch)
#        if ch == 'q':
#            print('输入q')
#            EPSEnableStatus = 0
#        elif ch == 'e':
#            print('输入e')
#            EPSEnableStatus = 1
#        elif ord(ch) == 0x03: # ctrl+c
#            print('shutdown')
#            break
#        #break
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
