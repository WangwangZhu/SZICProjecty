#! /usr/bin/env python3
#coding=utf-8
import serial
import csv
from time import sleep
import math
import struct
from collections import OrderedDict
###############################################################################################################
###############################################################################################################
# 文件名称：INSDataCollection.py
# 文件功能：获取INS通过串口发来的数据并且完成解析，将数据存放到字典里，同时，将数据写入到CSV文件
# 备注信息：
##############################################################################################################
##############################################################################################################
def recv(serial):
    global data
    while True:
        if serial.read() == b'\xaa':
            if serial.read() == b'\x55':
            #    if serial.read() == b'\x01':
            #        if serial.read() == b'\x58':
            #            if serial.read() == b'\x87':
            #                if serial.read() == b'\x00':
               # print('读到包头了')
                data = serial.read(135)
                data_sum = sum(data)-data[133]-data[134]
                if data[133] == (data_sum & 0xff):
                    if data[134] == (data_sum>>8 & 0xff):
                        print('校验通过')
                        sleep(0.02)
                        return data
                else:
                        print('校验不通过')
       # if data == '':
       #     continue
       # else:
       #     break

###############################################################################################################
# 函数名称：INSDataGet()
# 函数功能：解析数据,存储数据
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
def INSDataGet(qINSDATA):
    ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.5)
    if ser.isOpen():
        print('open success')
    else:
        print('open failed')

    insData = {}
    headers = ['gps_time','heading','pitch','roll','gyroX','gyroY','gyroZ','accX','accY','accZ',
                'latitude','longitude','east_speed','north_speed','position_type','GNSS_info1','GNSS_info2',
                'vehicle_lat_speed','vehicle_lon_speed']
    with open('../INS/example.csv','w',newline='') as f:
        writer = csv.DictWriter(f,headers)
        writer.writeheader()
        max_data_zhenghu = 0.0
        max_data_gaoqiong = 0.0
        while True:
            # global data 
            data =recv(ser)
            # 定义一个空的字典，用于存放解码后的数据

            # 偏移4：因为一个包开头有6个无用数据，头已经在读取函数中舍弃，因此再舍弃掉无用的四个数据
            gps_time = struct.unpack('<i',data[4+104:4+104+4])[0]
            heading = struct.unpack('<H',data[4+0:4+0+2])[0]*1e-2
            pitch = struct.unpack('<h',data[4+2:4+2+2])[0]*1e-2
            roll = struct.unpack('<h',data[4+4:4+4+2])[0]*1e-2

            gyroX = struct.unpack('<i',data[4+6:4+6+4])[0]*1e-5
            gyroY = struct.unpack('<i',data[4+10:4+10+4])[0]*1e-5
            gyroZ = struct.unpack('<i',data[4+14:4+14+4])[0]*1e-5

            accX = struct.unpack('<i',data[4+18:4+18+4])[0]*1e-6
            accY = struct.unpack('<i',data[4+22:4+22+4])[0]*1e-6
            accZ = struct.unpack('<l',data[4+26:4+26+4])[0]*1e-6
            latitude = struct.unpack('<q',data[4+42:4+42+8])[0] * 1e-9
            longitude = struct.unpack('<q',data[4+50:4+50+8])[0] * 1e-9
            east_speed = struct.unpack('<i',data[4+62:4+62+4])[0] * 1e-2
            north_speed = struct.unpack('<i',data[4+66:4+66+4])[0] * 1e-2
            rad_heanding = heading * math.pi /180
            vehicle_lon_speed = east_speed * math.sin(rad_heanding) + north_speed * math.cos(rad_heanding)
            vehicle_lat_speed = east_speed * math.cos(rad_heanding) + north_speed * math.sin(rad_heanding)
            position_type = struct.unpack('<B',data[4+113:4+113+1])[0]
            
            GNSS_info1 = struct.unpack('<B',data[4+108:4+108+1])[0] & 0x0f    
            GNSS_info2 = struct.unpack('<B',data[4+109:4+109+1])[0]
            row = {
                    'gps_time':gps_time, 
                    'heading':heading ,
                    'pitch':pitch ,
                    'roll':roll ,
                    'gyroX':gyroX ,
                    'gyroY':gyroY ,
                    'gyroZ':gyroZ ,
                    'accX':accX ,
                    'accY':accY ,
                    'accZ':accZ ,
                    'latitude':latitude ,
                    'longitude':longitude ,
                    'east_speed':east_speed ,
                    'north_speed':north_speed ,
                    'position_type':position_type ,
                    'GNSS_info1':GNSS_info1 ,
                    'GNSS_info2':GNSS_info2 ,
                    'vehicle_lat_speed':vehicle_lat_speed,
                    'vehicle_lon_speed':vehicle_lon_speed
                }
            #print(row['latitude'])
            #print(row['longitude'])
            row = OrderedDict(row)
            #print('纵向速度',end = ':')
            #print('sdfsfsd dfdddddddd')
            #print(type(row['vehicle_lon_speed']))
            #print(type(data))
            max_data_gaoqiong = (max(row['vehicle_lon_speed'],max_data_gaoqiong))
            #max_data_zhenghu = row['vehicle_lon_speed')
            print(max_data_gaoqiong*3.6)
            writer.writerow(row) # 将INS数据写入到CSV文件中，用于地图录制，地图录制完成后要及时关闭
            #for key in row: # 将INS数据发送到MPC进程中，用于轨迹跟踪
            qINSDATA.put(row) 
            print('INS进程已经把数据发送出去了'+str(row['gps_time']))
            #print('INS进程已把数据发出来了')

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
    ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.5)
    if ser.isOpen():
        print('open success')
    else:
        print('open failed')

    insData = {}
    headers = ['gps_time','heading','pitch','roll','gyroX','gyroY','gyroZ','accX','accY','accZ',
                'latitude','longitude','east_speed','north_speed','position_type','GNSS_info1','GNSS_info2',
                'vehicle_lat_speed','vehicle_lon_speed']
    with open('../INS/example.csv','w',newline='') as f:
        writer = csv.DictWriter(f,headers)
        writer.writeheader()
        max_data_zhenghu = 0.0
        max_data_gaoqiong = 0.0
        while True:
            # global data 
            data =recv(ser)
            # 定义一个空的字典，用于存放解码后的数据

            # 偏移4：因为一个包开头有6个无用数据，头已经在读取函数中舍弃，因此再舍弃掉无用的四个数据
            gps_time = struct.unpack('<i',data[4+104:4+104+4])[0]
            heading = struct.unpack('<H',data[4+0:4+0+2])[0]*1e-2
            pitch = struct.unpack('<h',data[4+2:4+2+2])[0]*1e-2
            roll = struct.unpack('<h',data[4+4:4+4+2])[0]*1e-2

            gyroX = struct.unpack('<i',data[4+6:4+6+4])[0]*1e-5
            gyroY = struct.unpack('<i',data[4+10:4+10+4])[0]*1e-5
            gyroZ = struct.unpack('<i',data[4+14:4+14+4])[0]*1e-5

            accX = struct.unpack('<i',data[4+18:4+18+4])[0]*1e-6
            accY = struct.unpack('<i',data[4+22:4+22+4])[0]*1e-6
            accZ = struct.unpack('<l',data[4+26:4+26+4])[0]*1e-6
            latitude = struct.unpack('<q',data[4+42:4+42+8])[0] * 1e-9
            longitude = struct.unpack('<q',data[4+50:4+50+8])[0] * 1e-9
            east_speed = struct.unpack('<i',data[4+62:4+62+4])[0] * 1e-2
            north_speed = struct.unpack('<i',data[4+66:4+66+4])[0] * 1e-2
            rad_heanding = heading * math.pi /180
            vehicle_lon_speed = east_speed * math.sin(rad_heanding) + north_speed * math.cos(rad_heanding)
            vehicle_lat_speed = east_speed * math.cos(rad_heanding) + north_speed * math.sin(rad_heanding)
            position_type = struct.unpack('<B',data[4+113:4+113+1])[0]
            
            GNSS_info1 = struct.unpack('<B',data[4+108:4+108+1])[0] & 0x0f    
            GNSS_info2 = struct.unpack('<B',data[4+109:4+109+1])[0]
            row = {
                    'gps_time':gps_time, 
                    'heading':heading ,
                    'pitch':pitch ,
                    'roll':roll ,
                    'gyroX':gyroX ,
                    'gyroY':gyroY ,
                    'gyroZ':gyroZ ,
                    'accX':accX ,
                    'accY':accY ,
                    'accZ':accZ ,
                    'latitude':latitude ,
                    'longitude':longitude ,
                    'east_speed':east_speed ,
                    'north_speed':north_speed ,
                    'position_type':position_type ,
                    'GNSS_info1':GNSS_info1 ,
                    'GNSS_info2':GNSS_info2 ,
                    'vehicle_lat_speed':vehicle_lat_speed,
                    'vehicle_lon_speed':vehicle_lon_speed
                }
            max_data_gaoqiong = (max(row['vehicle_lon_speed'],max_data_gaoqiong))
            print(max_data_gaoqiong*3.6)
            writer.writerow(row)














           # latitude =( data[4+42]*255**0 + data[4+42+1]*255**1+data[46+2]*255**2+data[46+3]*255**3+data[46+4]\
            #        *255**4 + data[46+5]*255**5 + data[46+6]*255**6 + data[46+7]*255**7) * 1e-9
            #latitude = int(''.join([str(n) for n in data[4+42:4+42+8].reverser()])) * 1e-9
#             def decodeIns(start,length,symbol):
#                global data
#                exponent = 0
#                outputData = 0
#                dataCopy = []
#                if symbol == 'unsigned':
#                    for i in range(4+start,4+start+length):
#                        outputData += data[i] * 255 ** exponent
#                        exponent = exponent+1
#                elif symbol == 'signed':
#                    if data[4+start+length] & 0x80:
#                        for i in range(4+start,4+start+length):
#                            if exponent == length-1:
#                                print('有符号数且为负数去掉符号')
#                                outputData += (data[i]&0x7f) * 255 ** exponent
#                            else:
#                                print('有符号数且为负数')
#                                outputData += (data[i]) * 255 ** exponent
#                            exponent = exponent+1
#                        outputData = -outputData
#                    else:
#                        print('有符号数但是数据为正')
#                        for i in range(4+start,4+start+length):
#                            outputData += data[i] * 255 ** exponent
#                            exponent = exponent+1
#                    
#                return outputData          # longitude = int(''.join([str(n) for n in data[4+50:4+50+8].reverser()])) * 1e-9


#            # gps_time = data[4+104:4+104+4]
#            #gps_time = decodeIns(104,4,'unsigned')
#            gps_time = struct.unpack('<i',data[4+104:4+104+4])[0]
#            # heading = float(data[4+0:4+0+2]) * 1e-2
#            #heading = decodeIns(0,2,'unsigned') * 1e-2
#            heading = struct.unpack('<H',data[4+0:4+0+2])[0]*1e-2
#            # pitch = data[4+2:4+2+2] * 1e-2
#            #pitch = decodeIns(2,2,'signed') * 1e-2
#            pitch = struct.unpack('<h',data[4+2:4+2+2])[0]*1e-2
#            # roll = data[4+4:4+4+2] * 1e-2
#            #roll = decodeIns(4,2,'signed') * 1e-2
#            roll = struct.unpack('<h',data[4+4:4+4+2])[0]*1e-2
#
#            # gyroX = data[4+6:4+6+4] * 1e-5
#            #gyroX = decodeIns(6,4,'signed') * 1e-5
#            gyroX = struct.unpack('<i',data[4+6:4+6+4])[0]*1e-5
#            # gyroY = data[4+10:4+10+4] * 1e-5
#            #gyroY = decodeIns(10,4,'signed') * 1e-5
#            gyroY = struct.unpack('<i',data[4+10:4+10+4])[0]*1e-5
#            # gyroZ = data[4+14:4+14+4] * 1e-5
#            #gyroZ = decodeIns(14,4,'signed') * 1e-5
#            gyroZ = struct.unpack('<i',data[4+14:4+14+4])[0]*1e-5
#
#            # accX = data[4+18:4+18+4] * 1e-6
#            #accX = decodeIns(18,4,'signed') * 1e-6
#            accX = struct.unpack('<i',data[4+18:4+18+4])[0]*1e-6
#            # accY = data[4+22:4+22+4] * 1e-6
#            #accY = decodeIns(22,4,'signed') * 1e-6
#            accY = struct.unpack('<i',data[4+22:4+22+4])[0]*1e-6
#            # accZ = data[4+26:4+26+4] * 1e-6
#            #accZ = decodeIns(26,4,'signed') * 1e-6
#            accZ = struct.unpack('<l',data[4+26:4+26+4])[0]*1e-6
#            #latitude = decodeIns(42,8,'unsigned') *1e-9
#            #longitude = decodeIns(50,8,'unsigned') * 1e-9
#            latitude = struct.unpack('<q',data[4+42:4+42+8])[0] * 1e-9
#            longitude = struct.unpack('<q',data[4+50:4+50+8])[0] * 1e-9
#            #print('struct '+ str(latitude))
#            #print(type(latitude[0]))
#            # east_speed = data[4+62:4+62+4] * 1e-2
#            #east_speed = decodeIns(62,4,'signed') *1e-2
#            east_speed = struct.unpack('<i',data[4+62:4+62+4])[0] * 1e-2
#            # north_speed = data[4+66:4+66+4] *1e-2
#            #north_speed = decodeIns(66,4,'signed') * 1e-2
#            north_speed = struct.unpack('<i',data[4+66:4+66+4])[0] * 1e-2
#            rad_heanding = heading * math.pi /180
#            vehicle_lon_speed = east_speed * math.sin(rad_heanding) + north_speed * math.cos(rad_heanding)
#            vehicle_lat_speed = east_speed * math.cos(rad_heanding) + north_speed * math.sin(rad_heanding)
#            # position_type = data[4+113:4+113+1]
#            #position_type = decodeIns(113,1,'unsigned')
#            position_type = struct.unpack('<B',data[4+113:4+113+1])[0]
#            
#            #GNSS_info1 = data[4+108:4+108+1]
#            #GNSS_info1 = decodeIns(108,1,'unsigned') & 0x0f
#            GNSS_info1 = struct.unpack('<B',data[4+108:4+108+1])[0] & 0x0f    
#            # GNSS_info1 = GNSS_info1 & 0x0f  # 详情查阅INS文档协议解析部分
#            # GNSS_info2 = data[4+109:4+109+1]
#            #GNSS_info2 = decodeIns(109,1,'unsigned')
