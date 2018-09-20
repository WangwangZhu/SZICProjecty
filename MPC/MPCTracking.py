#! /usr/bin/env python3
#coding=utf-8
###############################################################################################################
###############################################################################################################
# 文件名称：MPCTracking.py
# 文件功能：用于获取INS数据，并且传递给MPC轨迹跟踪器
# 备注信息：
##############################################################################################################
##############################################################################################################
import sys 
from multiprocessing import Process,Queue 
import numpy as np 
import csv
import threading
import time
from collections import OrderedDict 
###############################################################################################################
# 函数名称：
# 函数功能：
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
def MPCTrackingControler(qINSDATA):
    gps_time = None
    heading = None
    pitch = None
    roll = None
    gyroX = None
    gyroY = None
    gyroZ = None 
    accX = None 
    accY = None 
    accZ = None
    latitude = None 
    longitude = None 
    east_speed = None 
    north_speed = None 
    position_type = None 
    GNSS_info1 = None 
    GNSS_info2 = None 
    vehicle_lat_speed = None 
    vehicle_lon_speed = None
    lock = threading.Lock() 
    print('进入MPC进程了')
    def MPCINSDataReceive():
        nonlocal gps_time 
        nonlocal heading 
        nonlocal pitch 
        nonlocal roll 
        nonlocal gyroX 
        nonlocal gyroY 
        nonlocal gyroZ  
        nonlocal accX  
        nonlocal accY  
        nonlocal accZ  
        nonlocal latitude  
        nonlocal longitude  
        nonlocal east_speed  
        nonlocal north_speed  
        nonlocal position_type  
        nonlocal GNSS_info1   
        nonlocal GNSS_info2 
        nonlocal vehicle_lat_speed  
        nonlocal vehicle_lon_speed 
        value = []
        i = 0
        with open('./INSDataInMpc.csv','w',newline='') as f:
            writer = csv.DictWriter(f,headers)
            writer.writeheader()
            while True:
                writer.writerow(value) 
                value = qINSDATA.get(True)
                lock.acquire()
                try:
                    #qINSDATA.queue.clear()
                    gps_time = value['gps_time']
                    heading = value['heading']
                    pitch = value['pitch']
                    roll = value['roll']
                    gyroX = value['gyroX']
                    gyroY = value['gyroY']
                    gyroZ = value['gyroZ']
                    accX = value['accX']
                    accY = value['accY']
                    accZ = value['accZ']
                    latitude = value['latitude'] 
                    longitude = value['longitude']
                    east_speed = value['east_speed']
                    north_speed = value['north_speed']
                    position_type = value['position_type']
                    GNSS_info1 = value['GNSS_info1']
                    GNSS_info2 = value['GNSS_info2']
                    vehicle_lat_speed = value['vehicle_lat_speed'] 
                    vehicle_lon_speed = value['vehicle_lon_speed']
                finally:
                    lock.release()

                print('收到数据并且打印出来了，在MPC进程里面'+str(value['gps_time']) +'   '+ str(qINSDATA.qsize()))
    MPCINSDataReceive()
    





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
# if __name__ == '__main__':


















###############################################################################################################
# 函数名称：
# 函数功能：
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################

#       headers = ['gps_time','heading','pitch','roll','gyroX','gyroY','gyroZ','accX','accY','accZ',
#                'latitude','longitude','east_speed','north_speed','position_type','GNSS_info1','GNSS_info2',
#                'vehicle_lat_speed','vehicle_lon_speed']

#                value.append(qINSDATA.get(True))
#                i = i+1
#                if i == 19:
#                    i = 0
#
#                row = {
#                    'gps_time':gps_time, 
#                    'heading':heading ,
#                    'pitch':pitch ,
#                    'roll':roll ,
#                    'gyroX':gyroX ,
#                    'gyroY':gyroY ,
#                    'gyroZ':gyroZ ,
#                    'accX':accX ,
#                    'accY':accY ,
#                    'accZ':accZ ,
#                    'latitude':latitude ,
#                    'longitude':longitude ,
#                    'east_speed':east_speed ,
#                    'north_speed':north_speed ,
#                    'position_type':position_type ,
#                    'GNSS_info1':GNSS_info1 ,
#                    'GNSS_info2':GNSS_info2 ,
#                    'vehicle_lat_speed':vehicle_lat_speed,
#                    'vehicle_lon_speed':vehicle_lon_speed
#                }
#                row = OrderedDict(row)
 
