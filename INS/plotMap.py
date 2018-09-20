#! /usr/bin/env python3
#coding=utf-8
###############################################################################################################
###############################################################################################################
# 文件名称：plotMap.py
# 文件功能：用于可视化地图数据
# 备注信息：'gps_time','heading','pitch','roll','gyroX','gyroY','gyroZ','accX','accY','accZ',
#           'latitude','longitude','east_speed','north_speed','position_type','GNSS_info1','GNSS_info2',
#           'vehicle_lat_speed','vehicle_lon_speed'
###############################################################################################################
###############################################################################################################
import matplotlib.pyplot as plt
import csv
import numpy as np
###############################################################################################################
# 函数名称：ReadDataFromCSV()
# 函数功能：读取相关的INS数据到相关的数组中
# 输入参数：
# 返回值  ：
# 备注信息：
###############################################################################################################
latitude = []
longitude = []
heading = []
def ReadDataFromCSV():
    global latitude
    global longitude
    global heading 
    with open('/home/zhu/Desktop/SZICProject/INS/MPCTracking.csv','r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            column1 = float((row['latitude']))
            column2 = float((row['longitude']))
            column3 = float(row['heading'])
            latitude.append(column1)
            longitude.append(column2)
            heading.append(column3)
            # print(column1,'   ',column2) 

###############################################################################################################
# 函数名称：DropHeading
# 函数功能：绘制车辆的方位角
# 输入参数：
# 返回值  ：
# 备注信息：方位角越过360后会发生一次突变
###############################################################################################################
def DropHeading(heading):
    minHead = min(heading)
    maxHead = max(heading)
    plt.plot(heading)
    plt.title('Heading Angle')
    plt.xticks(np.arange(0,len(heading),len(heading)/5))
    plt.yticks(np.arange(minHead,maxHead+5,(maxHead-minHead)/5))
    plt.grid()
    plt.show()
###############################################################################################################
# 函数名称：DropLatitudeLongitude
# 函数功能：绘制车辆的经纬度信息
# 输入参数：
# 返回值  ：
# 备注信息：
###############################################################################################################
def DropLatitudeLongitude(latitude,longitude):
    minLat = min(latitude)
    maxLat = max(latitude)
    minLon = min(longitude)
    maxLon = max(longitude)
    plt.figure(num = '经纬度')
    plt.title('Map')
    plt.scatter(latitude,longitude)
    plt.xlim(minLat,maxLat)
    plt.ylim(minLon,maxLon)
    plt.xticks(np.arange(minLat,maxLat,0.0003))
    plt.yticks(np.arange(minLon,maxLon,0.0003))
    plt.show()
###############################################################################################################
# 程序执行主体
###############################################################################################################

###############################################################################################################
# 函数名称：__main__()
# 函数功能：主调函数
# 输入参数：
# 返回值  ：
# 备注信息：
###############################################################################################################
if __name__ == '__main__':
    ReadDataFromCSV()
    DropHeading(heading)
    DropLatitudeLongitude(latitude,longitude)

###############################################################################################################
# 程序执行主体
###############################################################################################################

###############################################################################################################
# 函数名称：__main__()
# 函数功能：主调函数
