# /usr/bin/env python3
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
sys.path.append(r'../CAN')
sys.path.append(r'../INS')
sys.path.append(r'../MPC')
sys.path.append(r'../KeyBoardMonitor')
sys.path.append(r'../Cameras')
sys.path.append(r'../Lidar')
sys.path.append(r'../Visualization')
sys.path.append(r'./CAN')
sys.path.append(r'./INS')
sys.path.append(r'./MPC')
sys.path.append(r'./KeyBoardMonitor')
sys.path.append(r'./Cameras')
sys.path.append(r'./Lidar')
sys.path.append(r'./Visualization')
import time 
import sendReceiveByDbc
import INSDataCollection
import MPCTracking 
import keyBoardMonitor
import VisualizationClass
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
    graph = VisualizationClass.StreamDetectionPlot()
    graph.initPlot()
    qKeyBoardEPSEBSEnable = Queue()
    qCANDATA = Queue()
    qINSDATA = Queue()
    #p1 = Process(target=sendReceiveByDbc.SendCan,args = (qCANDATA,qKeyBoardEPSEBSEnable))
    #p2 = Process(target=keyBoardMonitor.InputKey,args=(qKeyBoardEPSEBSEnable,graph))#将graph传入，用于关闭交互式绘图
    p3 = Process(target=INSDataCollection.INSDataGet,args=(qINSDATA,))
    #p4 = Process(target=MPCTracking.MPCTrackingControler,args=(qINSDATA,))
    p5 = Process(target=graph.acceptInsDataPlot,args=(qINSDATA,))
    #p1.start()
    #p2.start()
    p3.start()
    #p4.start()
    p5.start()
    qCANDATA.put(0)
    qCANDATA.put(0)
    qCANDATA.put(00)
#    parser = argparse.ArgumentParser(description = 'Create a database from scratch.')
#    parser.add_argument('filename',help=('The filename to save to the database to.'))
#    parser.add_argument('-n','--name',default='Engine example',help=('The name of the database(not filename, the internal name)'))
#    args = parser.parse_args()
#
#    createDatabase(args.name,args.filename)






    #graph.acceptInsDataPlot(qINSDATA)

#    filePath =r'/home/zhu/Desktop/SZICProject/INS/MPCTracking.csv'
#    with open(filePath) as f:
#        reader = csv.DictReader(f)
#        gps_time = []
#        vehicle_lon_speed = []
#        predict_a = []
#        anomalyScore_a = []
#        heading = []
#        latitude = []
#        longitude = []
#        for row in reader:
#            gps_time_now = int(row['gps_time'])
#            vehicle_lon_speed_now = float(row['vehicle_lon_speed'])
#            heading_now = float(row['heading'])
#            latitude_now = float(row['latitude'])
#            longitude_now = float(row['longitude'])
#            # 添加到列表里
#            gps_time.append(gps_time_now)
#            vehicle_lon_speed.append(vehicle_lon_speed_now)
#            heading.append(heading_now)
#            latitude.append(latitude_now)
#            longitude.append(longitude_now)
#    for i in range(len(gps_time)-1):
#        graph.anomalyDetectionPlot(gps_time[i],vehicle_lon_speed[i],heading[i],latitude[i],longitude[i])
#        #time.sleep(0.05)
#    graph.close()
#    time.sleep(1000)
#
#
#
#
#




###############################################################################################################
# 函数名称：
# 函数功能：
# 输入参数：
# 返回值  ：
# 备注信息：
##############################################################################################################


#import numpy as np
#
#npose = 5
#nsmile = 2
#
#poseSmile_cell = np.empty((npose,nsmile),dtype=object)
#
#for i in range(5):
#    for k in range(2):
#        poseSmile_cell[i,k] = np.zeros((4,4))
#
#print(poseSmile_cell[1,1].shape)
#print(np.asmatrix(poseSmile_cell).shape)
#print(poseSmile_cell.shape)
#print(poseSmile_cell)

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 13:18:42 2018

@author: 13120
"""
import scipy as sp 
import numpy as np 
import pandas as pd 

Nx = 6  # 状态变量的个数，这里的状态变量个数是指的车辆模型的状态变量的个数，
        # 需要区别于S函数的状态变量，两者不是一码事；
Nu = 1  # 控制量的个数，转角 
Ny = 2  # 输出量的个数,Y 和 航向角 
# 输入接口转换，x_dot后面加一个非常小的数是为了防止出现分母为零的情况 
y_dot   = 0.001  # 车辆横向速度 
x_dot   = 0.001 + 0.00001  # 车辆纵向速度 
phi     = 0.001  # 车辆横摆角 
phi_dot = 0.001  # 车辆横摆角速度 
Y       = 0.001  # 车辆纵向位置 
X       = 0.001  # 车辆横向位置 
 
# 读入局部路径规划器的数据，传递进来的是5次曲线的参数 
#Paramater_X_Y(1:5,1)   = ???  
#Paramater_X_phi(1:5,1) = ??? 
 
Np      = 6 # 预测步长 
Nc      = 2 # 控制步长 
T       = 0.02 # 仿真步长  
# MPC的CostFunctionde 权重矩阵为[2*2]对角阵,Q1,Q2 为对角线上的元素 
# MPC的CostFunctionde 权重矩阵为[2*2]对角阵,Q1,Q2 为对角线上的元素  
Q1      = 200  
Q2      = 1000  
R1      = 5000  # 权重矩阵 
Rou     = 1000  # 松弛因子 
StateAviodance = 1  # 是否开启避障功能的状态机 
 
##车辆参数输入 
# 前后轮的滑移率  
Sf = 0.2  
Sr = 0.2  
# 前后车轮距离车辆质心的距离，输入车辆的固有属性 
lf = 1.232   
lr = 1.468   
# 前后车轮的纵横向侧偏刚度，车辆固有属性   
Ccf = 66900  
Ccr = 62700  
Clf = 66900  
Clr = 62700  
# m为车辆质量，g为重力加速度，I为车辆绕Z轴的转动惯量，车辆的固有属性 
m = 1723  
g = 9.8  
I = 4175  
# delta_f = 0; 
# 矩阵转换，控制量与状态量合在一起 
kesi = np.zeros(Nx+Nu)  
kesi[1] = y_dot  
kesi[2] = x_dot  
kesi[3] = phi  
kesi[4] = phi_dot  
kesi[5] = Y  
kesi[6] = X  
# 该量为车辆的前轮偏角，优化得出的控制序列是前轮偏角的增量， 
# 参考课本P78页，优化得出的结果是偏角还是偏角增量由目标函数的形式决定。 
#kesi[7] = U(1)   
#delta_f = U(1)  
# 权重矩阵设置 
Q_cell = np.zeros(shape = (1,Np*Ny+1)) 
Q_cell_Row = np.zeros(shape = (Ny,1)) 
Q_cell_NoZeros = np.array([[Q1,0],[0,Q2]]) 
Q_cell_Zeros = np.zeros(shape = (Ny,Ny)) 
for i in range(0,Np):     
#i=0 
    for j in range(0,Np): 
        if i == j: 
            Q_cell_Row = np.concatenate((Q_cell_Row,Q_cell_NoZeros),axis = 1) 
        else: 
            Q_cell_Row = np.concatenate((Q_cell_Row,Q_cell_Zeros),axis = 1) 
    Q_cell = np.concatenate((Q_cell,Q_cell_Row),axis = 0) 
    Q_cell_Row = np.zeros(shape = (Ny,1)) 
Q_cell = np.delete(Q_cell,[0],axis =1)  
Q_cell = np.delete(Q_cell,[0],axis =0)  
print(Q_cell) 
print(Q_cell.shape) 
