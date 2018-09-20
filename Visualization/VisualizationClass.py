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
import os
import datetime
import matplotlib.pyplot as plt
#plt.rcParams['font.sans-serif']=['SimHei']
#plt.rcParams['axes.unicode_minus']=False
from matplotlib.animation import FuncAnimation
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker

###############################################################################################################
# 类名称：
# 类功能：
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
class StreamDetectionPlot(object):
    def __init__(self):
        # 打开交互式绘图
        plt.ion()
        # 设置绘图的基本变量
        self.gps_time = []
        self.gps_timeRange = []
        self.vehicle_lon_speed = []
        self.heading = []
        self.latitude = []
        self.longitude = []
        self.vehicle_lon_speedRange = []
        self.accX = []
        # 初始化绘图
        global fig
        fig = plt.figure(facecolor='white') # figsize=(18,8),
        fig.subplots_adjust(left=0.06,right=0.94)
        self.INS_longitudeSpeed = fig.add_subplot(2,2,1)
        self.INS_heading = fig.add_subplot(2,2,2)
        self.INS_longitudeAcc = fig.add_subplot(2,2,3)
        self.INS_LatitudeLongitude = fig.add_subplot(2,2,4)

    # 定义初始的绘图方法
    def initPlot(self):
        # 初始化longitudeSpeedLine两条
        self.longitudeSpeedLine, = self.INS_longitudeSpeed.plot(self.gps_time,self.vehicle_lon_speed,
                linestyle = '-',color = 'red',label = 'longitude speed')
        self.INS_longitudeSpeed.set_title('Longitude Speed')
        self.INS_longitudeSpeed.legend(loc='upper right',frameon=False)
        self.INS_longitudeSpeed.grid(True)
        #self.INS_longitudeSpeed.set_ylabel([])
        self.INS_longitudeSpeed.set_xticks([])
        
        self.headingLine, = self.INS_heading.plot(self.gps_time,self.heading,
                linestyle = '-',color = 'blue',label = 'heading value')
        self.INS_heading.set_title('Heading Angle')
        self.INS_heading.legend(loc='upper right',frameon=False)
        self.INS_heading.grid(True)
        #self.INS_heading.set_ylabel([])
        self.INS_heading.set_xticks([])
        
        self.accXLine, = self.INS_longitudeAcc.plot(self.gps_time,self.accX,
                linestyle = '-',color = 'blue',label = 'longitude acceleration')
        self.INS_longitudeAcc.set_title('longitude accelaration')
        self.INS_longitudeAcc.legend(loc='upper right',frameon=False)
        self.INS_longitudeAcc.grid(True)
        #self.INS_longitudeAcc.set_ylabel([])
        self.INS_longitudeAcc.set_xticks([])
         
        self.latitudelongitude, = self.INS_LatitudeLongitude.plot(self.latitude,self.longitude,
                linestyle = '-',color = 'blue',label = 'position')
        self.INS_LatitudeLongitude.set_title('position')
        self.INS_LatitudeLongitude.legend(loc='upper right',frameon=False)
        self.INS_LatitudeLongitude.grid(True)
        #self.INS_LatitudeLongitude.set_ylabel([])
        self.INS_LatitudeLongitude.set_xticks([])       
        
        
        # 初始化anomalyScoreLine两条
        #self.anomalyScoreLine, = self.INS_LatitudeLongitude.plot(self.gps_time,self.vehicle_lon_speed,
        #        linestyle = '-',color = 'red',label = 'anomaly score')
        #self.INS_heading.legend(loc='upper right',frameon=False)
        #self.baseline = self.INS_heading.axhline(0.8,color = 'black',lw = 2)

        # 设置前面两幅图的x,y坐标
        #self.INS_heading.set_xlabel('datetime')
        #self.INS_heading.set_ylabel('anomaly score')
        
        # 配置坐标轴的显示
        #self.anomalyValueTableColumnsName = ['gps_time','actual value','expect value','anomaly score']
        #self.anomalyValueTable.text(0.05,0.99,'Anomaly Value Table',size = 12)
        #self.anomalyValueTable.set_xticks([])
        #self.anomalyValueTable.set_yticks([])
        
    # 定义输出方法
    def anomalyDetectionPlot(self,gps_time,vehicle_lon_speed,heading,latitude,longitude):
        # 更新绘制图像的值
        self.gps_time.append(gps_time)
        self.vehicle_lon_speed.append(vehicle_lon_speed)
        self.heading.append(heading)
        self.latitude.append(latitude)
        self.longitude.append(longitude)
        if len(self.gps_time) >= 2000:
            self.gps_time.pop(0)
            self.vehicle_lon_speed.pop(0)
            self.latitude.pop(0)
            self.longitude.pop(0)
            self.heading.pop(0)
        print(len(self.gps_time))
        ##################################################################################
        # 绘制车辆纵向速度与GPS时间的关系
        # 更新x,y轴的范围
        self.gps_timeRange = [min(self.gps_time),max(self.gps_time)+80]
        self.vehicle_lon_speedRange = [min(self.vehicle_lon_speed),max(self.vehicle_lon_speed)+1]
        # 更新x,y轴的显示范围
        self.INS_longitudeSpeed.set_xlim(self.gps_timeRange[1]-4000,self.gps_timeRange[1])
        self.INS_longitudeSpeed.set_ylim(self.vehicle_lon_speedRange[0],self.vehicle_lon_speedRange[1])
        # 绘制纵轴
        self.INS_longitudeSpeed.set_xticks(range(self.gps_timeRange[1]-4000,self.gps_timeRange[1],800))
        self.INS_longitudeSpeed.set_yticks(range(0,24,4))
        # 更新参数
        self.longitudeSpeedLine.set_xdata(self.gps_time)
        self.longitudeSpeedLine.set_ydata(self.vehicle_lon_speed)
        ###################################################################################
        # 绘制车辆航向角与GPS时间的关系
        # 更新x,y轴的范围
        self.heading_timeRange = [min(self.heading),max(self.heading)+80]
        self.headingRange = [min(self.heading),max(self.heading)+1]
        # 更新x,y轴的显示范围
        self.INS_heading.set_xlim(self.gps_timeRange[1]-4000,self.gps_timeRange[1])
        self.INS_heading.set_ylim(self.headingRange[0],self.headingRange[1])
        # 绘制纵轴
        self.INS_heading.set_xticks(range(self.gps_timeRange[1]-4000,self.gps_timeRange[1],800))
        self.INS_heading.set_yticks(range(-20,360,76)) # 一共分5格
        # 更新参数
        self.headingLine.set_xdata(self.gps_time)
        self.headingLine.set_ydata(self.heading)
        ###################################################################################
        # 绘制车辆纵向加速度与GPS时间的关系
        # 更新x,y轴的范围
#        self.gps_timeRange = [min(self.gps_time),max(self.gps_time)+80]
#        self.vehicle_lon_speedRange = [min(self.vehicle_lon_speed),max(self.vehicle_lon_speed)+1]
#        # 更新x,y轴的显示范围
#        self.INS_LatitudeLongitude.set_xlim(self.gps_timeRange[1]-4000,self.gps_timeRange[1])
#        self.INS_LatitudeLongitude.set_ylim(self.vehicle_lon_speedRange[0],self.vehicle_lon_speedRange[1])
#        # 绘制纵轴
#        self.INS_LatitudeLongitude.set_xticks(range(self.gps_timeRange[1]-4000,self.gps_timeRange[1],800))
#        self.INS_LatitudeLongitude.set_yticks(range(0,24,4))
#        # 更新参数
#        self.longitudeSpeedLine.set_xdata(self.gps_time)
#        self.longitudeSpeedLine.set_ydata(self.vehicle_lon_speed)
        ###################################################################################
        # 绘制经纬度信息
        # 更新x,y轴的范围
                
        self.latitude_Range = [min(self.latitude)-0.0005,max(self.latitude)]
        self.longitude_Range = [min(self.longitude)-0.001,max(self.longitude)+0.001]
        # 更新x,y轴的显示范围
        self.INS_LatitudeLongitude.set_xlim(self.latitude_Range[0],self.latitude_Range[1])
        self.INS_LatitudeLongitude.set_ylim(self.longitude_Range[0],self.longitude_Range[1])
        # 绘制纵轴
        self.INS_LatitudeLongitude.set_xticks(np.arange(self.latitude_Range[0],self.latitude_Range[1],0.0003))
        self.INS_LatitudeLongitude.set_yticks(np.arange(self.longitude_Range[0],self.longitude_Range[1],0.0003))
        # 更新参数
        self.latitudelongitude.set_xdata(self.latitude)
        self.latitudelongitude.set_ydata(self.longitude)        
        ################################################################
        
        # 绘图间隔
        plt.pause(0.05)
        plt.draw()

    def close(self):
        plt.ioff()
        plt.show()


###############################################################################################################
# 函数名称：__main__()
# 函数功能：主调函数
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################
if __name__ == '__main__':
    
    filePath =r'/home/zhu/Desktop/SZICProject/INS/MPCTracking.csv'
    with open(filePath) as f:
        reader = csv.DictReader(f)
        gps_time = []
        vehicle_lon_speed = []
        predict_a = []
        anomalyScore_a = []
        heading = []
        latitude = []
        longitude = []
        for row in reader:
            gps_time_now = int(row['gps_time'])
            vehicle_lon_speed_now = float(row['vehicle_lon_speed'])
            heading_now = float(row['heading'])
            latitude_now = float(row['latitude'])
            longitude_now = float(row['longitude'])
            # 添加到列表里
            gps_time.append(gps_time_now)
            vehicle_lon_speed.append(vehicle_lon_speed_now)
            heading.append(heading_now)
            latitude.append(latitude_now)
            longitude.append(longitude_now)
    graph = StreamDetectionPlot()
    graph.initPlot()
    for i in range(len(gps_time)-1):
        graph.anomalyDetectionPlot(gps_time[i],vehicle_lon_speed[i],heading[i],latitude[i],longitude[i])
        #time.sleep(0.05)
    graph.close()








''''

        # 更新绘制图像的值
        self.gps_time.append(gps_time)
        self.vehicle_lon_speed.append(vehicle_lon_speed)
        self.predictValue.append(predictValue)
        self.anomalyScore.append(anomalyScore)

        # 更新x,y轴的范围
        self.gps_timeRange = [min(self.gps_time),max(self.gps_time)+80]
        self.vehicle_lon_speedRange = [min(self.vehicle_lon_speed),
                max(self.vehicle_lon_speed)+1]
        #self.predictValueRange = [min(self.predictValue),max(self.predictValue)+1]
        
        # 更新x,y轴的显示范围
        self.INS_longitudeSpeed.set_xlim(self.gps_timeRange[1]-1000,self.gps_timeRange[1])
        self.INS_longitudeSpeed.set_ylim(self.vehicle_lon_speedRange[0],
                self.vehicle_lon_speedRange[1])
        #self.INS_heading.set_ylim(self.anomalyScoreRange[0],self.anomalyScoreRange[1])
        #self.INS_heading.set_xlim(self.gps_timeRange[1]-60,self.gps_timeRange[1])
        
        self.INS_longitudeSpeed.set_yticks(range(0,24,4))
        # 更新longitudeSpeedLine两条线
        self.longitudeSpeedLine.set_xdata(self.gps_time)
        self.longitudeSpeedLine.set_ydata(self.vehicle_lon_speed)
        #self.predictLine.set_xdata(self.gps_time)
        #self.predictLine.set_ydata(self.predictValue)

        # 更新anomaly线
        #self.anomalyScoreLine.set_xdata(self.gps_time)
        #self.anomalyScoreLine.set_ydata(self.anomalyScore)




        self.INS_LatitudeLongitude.set_xticks([])
        self.INS_LatitudeLongitude.set_yticks([])





































#    plt.figure(num= 'ceshi')
#    plt.grid(True)
#    plt.plot(gps_time,vehicle_lon_speed)
#    plt.xticks([])
#    plt.yticks([])
#    plt.show()
#
#    print('chengxujieshu ')
#
#        # 更新散点图
#        if anomalyScore >= 0.8:
#           self.anomalyScatterX.append(gps_time)
#           self.anomalyScatterY.append(acutalValue)
#           self.INS_longitudeSpeed.scatter(self.anomalyScatterX,self.anomalyScatterY,
#                   s=50,color='black')
#        
#        # 更新anomaly的高亮线
#        if anomalyScore >= 0.8:
#            self.highlightList.append(gps_time)
#            self.highlightListTurnOn = True
#        else:
#            self.highlightListTurnOn = False 
#        if len(self.highlightList) != 0 and self.highlightListTurnOn is False:
#            self.INS_heading.axvspan(self.highlightList[0]-40,
#                    self.highlightList[-1]+40,
#                    color='r',edgecolor=None,alpha=0.2)
#            self.highlightList = []
#            self.highlightListTurnOn = True 
#        
#        # 更新anomaly value table
#        if anomalyScore >= 0.8:
#            # 移除table，然后重新绘制
#            self.anomalyValueTabel.remove()
#            self.anomalyValueTabel = fig.add_axes([0.8,0.1,0.2,0.8],frameon=False)
#            self.anomalyValueTableColumnsName = ['gps_time','actual value','expect value',
#                    'anomaly score']
#            self.anomalyValueTabel.text(0.05,0.99,'Anomaly Value Table',size=12)
#            self.anomalyValueTabel.set_xticks([])
#            self.anomalyValueTabel.set_yticks([])
#            self.tableValue.append(gps_time,vehicle_lon_speed,predictValue,anomalyScore)
#            if len(self.tableValue) >= 40 : self.tableValue.pop(0)
#            self.anomalyValueTabel.table(cellText=self.tableValue,colWidth=[0.35]*4,
#                    colLabels = self.anomalyValueTableColumnsName,loc=1,cellLoc='center')


'''


    





















