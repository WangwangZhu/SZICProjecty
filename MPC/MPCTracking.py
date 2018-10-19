#! /usr/bin/env python3
#coding=utf-8
###############################################################################################################
###############################################################################################################
# 文件名称：MPCTracking.py
# 文件功能：MPC轨迹跟踪器
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
import threading
import scipy as sp 
import pandas as pd
import math
###############################################################################################################
# 函数名称：
# 函数功能：
# 输入参数：
# 返回值  ：
# 备注信息：因为观光车平台缺少车载传感器，车辆的状态信息主要来自组合导航数据
##############################################################################################################
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


Nx = 6  # 状态变量的个数，这里的状态变量个数是指的车辆模型的状态变量的个数
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
Nc      = 3 # 控制步长
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
kesi[0] = y_dot 
kesi[1] = x_dot 
kesi[2] = phi 
kesi[3] = phi_dot 
kesi[4] = Y 
kesi[5] = X 
# 该量为车辆的前轮偏角，优化得出的控制序列是前轮偏角的增量，
# 参考课本P78页，优化得出的结果是偏角还是偏角增量由目标函数的形式决定。
#kesi[6] = 这里需要填写控制增量
delta_f = 0 # 这里需要填写控制增量 
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

R = R1 * np.eye(Nu*Nc)
print(R)

# 系统状态转移矩阵
a = np.matrix([
        [1-(2*(Ccf+Ccr)*T)/(m*x_dot), T*(-phi_dot+2*(Ccf*(y_dot+lf*phi_dot)+Ccr*(y_dot-lr*phi_dot))/(m*x_dot**2)),  0,-T*(x_dot-2*(lr*Ccr-lf*Ccf)/(m*x_dot)),  0,  0],
        [T*(phi_dot-(2*Ccf*delta_f)/(m*x_dot)), (2*Ccf*T*delta_f*(lf*phi_dot+y_dot))/(m*x_dot**2)+1, 0, T*(y_dot-(2*lf*Ccf*delta_f)/(m*x_dot)),  0,  0],
        [0, 0, 1, T, 0,  0],
        [(2*(lr*Ccr-lf*Ccf)*T)/(I*x_dot), T*2*(lf*Ccf*(y_dot+lf*phi_dot)-lr*Ccr*(y_dot-lr*phi_dot))/(I*x_dot**2), 0, 1-((lf**2*Ccf+lr**2*Ccr)*T)/(I*x_dot), 0,  0],
        [T*math.cos(phi), T*math.sin(phi),  T*(x_dot*math.cos(phi)-y_dot*math.sin(phi)), 0, 1,  0],
        [-T*math.sin(phi),  T*math.cos(phi), -T*(y_dot*math.cos(phi)+x_dot*math.sin(phi)),  0, 0,  1],
        ])
b = np.matrix([
        [2*Ccf*T/m],
        [T*2*Ccf*(2*delta_f-(y_dot+lf*phi_dot)/(x_dot))/(m*x_dot)],
        [0],
        [2*lf*Ccf*T/I],
        [0],
        [0],
        ])
print(a.shape)
print()

print(b.shape)
A_1 = np.hstack((a,b))
A_2_1 = np.zeros((Nu,Nx))
A_2_2 = np.eye(Nu)
A_2 = np.hstack((A_2_1,A_2_2))
A = np.vstack((A_1,A_2))
B_2 = np.eye(Nu)
B = np.vstack((b,B_2))
print(A.shape)
print(B.shape)
C = np.matrix([[0,0,1,0,0,0,0],[0,0,0,0,1,0,0]]) # 输出矩阵
print(C.shape)
''''
    A_cell = cell(2,2)
    B_cell = cell(2,1)
    A_cell{1,1} = a
    A_cell{1,2} = b
    A_cell{2,1} = zeros(Nu,Nx)
    A_cell{2,2} = eye(Nu)
    B_cell{1,1} = b
    B_cell{2,1} = eye(Nu)
    A = cell2mat(A_cell)
    B = cell2mat(B_cell)
    C = [0 0 1 0 0 0 0;0 0 0 0 1 0 0];
'''
# 构造目标函数，构造QP问题的目标函数
PSI = []
THETA = []
for j in range(Np):
    if j == 0:
        PSI = np.linalg.matrix_power(A,j+1)
    else:
        PSI = np.vstack((PSI,np.linalg.matrix_power(A,j+1)))
    THETA_h = []
    for k in range(Nc):
        if k<=j:
            A_e = np.linalg.matrix_power(A,j-k)
            C_A = np.dot(C,A_e)
            if k == 0:
                THETA_h =np.dot(C_A,B) 
            else:
                THETA_h = np.hstack((THETA_h,np.dot(C_A,B)))
        else:
            THETA_h = np.hstack((THETA_h,np.zeros(Ny,Nu)))
    THETA = np.vstack((THETA,THETA_h))

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

