# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 17:07:26 2024

@author: kcy
"""

import matplotlib as mpl
import matplotlib.pyplot as plt 
from scipy import interpolate
import math
from scipy import misc
import time
import numpy as np
import os
import cmocean
import statistics
from scipy.optimize import curve_fit

# 定义拟合函数，注意这里的x0是固定的
def parabola(x, a, c):
    return a * (x - x0)**2 + c

if __name__=="__main__": 
    print ("开始",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    num_curves = 90
    colors = cmocean.cm.balance(np.linspace(0, 1, num_curves))  # 使用Viridis颜色映射
    for angle in range (10,80,10):
        # X_axis = np.array([19, 20, 21, 22, 23])   
        x0 = 7  #固定对称轴的位置,假设对称轴在 x = 7
        Derivative_zero = []
        # add_current_ddm = [[0 for x in range(45)]  for x in range(160)] 
        # add_current_ddm  = np.array( add_current_ddm , dtype=np.float32) 
        direction_s = 240#计算船舶方向参数  
        zoom_factor = (20,3)
        for k in range (int(len(ddm_all)*0.15),len(ddm_all)-500,1):
            current_ddm = ddm_all[k]      
            #计算船舶方向角
            ship_direction = calculate_azimuth(np.array([(infor_all[k+direction_s][8]-infor_all[k][8]), (infor_all[k+direction_s][7]-infor_all[k][7]),]))
            if(ship_direction>90):
                antenna_direction = ship_direction-90
            else:
                antenna_direction = ship_direction+270         
            mix_direction = calculate_jiajiao(infor_all[k][3],antenna_direction)
            #限制高度角及方向角
            if(np.max(current_ddm)>8000 and mix_direction<30 and infor_all[k][2]>angle and infor_all[k][2]<angle+10):
                Derivative_zero_point = [0 for x in range(15)]
                Derivative_zero_point = np.array(Derivative_zero_point, dtype=np.float32) 
                # zoomed_current_ddm = zoom(current_ddm, zoom_factor, order=3)  # order=3表示使用三次样条插值
                # zoomed_current_ddm = zoomed_current_ddm/np.max(zoomed_current_ddm)
                # add_current_ddm = add_current_ddm + zoomed_current_ddm[400:560]
                for j in range (0,15,1):
                    #开始二次多项式拟合
                    x_12 = np.array([14,15,16,17,18,19,20,21,22,23,24,25])
                    y_12 = np.array(current_ddm[:,j][14:26])
                    # 使用curve_fit进行拟合
                    coefficients = np.polyfit(x_12, y_12, 2)  # 2代表二次多项式y=ax2+bx+c模式
                    Derivative_zero_point[j] = -coefficients[1]/(coefficients[0]*2)
                if(max(Derivative_zero_point)<24 and min(Derivative_zero_point)>19):
                    Derivative_zero.append(Derivative_zero_point)
        Derivative_zero = np.array( Derivative_zero, dtype=np.float32) 
        for j in range (0,15,1):
            Derivative_zero_point[j] = sum(Derivative_zero[:,j])/len(Derivative_zero[:,j])
        x_axis = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
        y_axis = Derivative_zero_point
        params, covariance = curve_fit(parabola, x_axis, y_axis)
        a, c = params
        x_fit = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
        x_fit = np.array(x_fit, dtype=np.float32)
        y_fit = parabola(x_fit, a, c)
        plt.plot(np.linspace(-500, 500, 15), -y_fit, color=colors[angle], alpha=0.7)
    plt.savefig('E:/1.5.2.png', dpi=512)
     
    print ("结束",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

def calculate_azimuth(vector):#输出一个以正北为0度的顺时针方向
    # 提取x和y分量
    x, y = vector[0], vector[1]   
    # 计算方位角，使用arctan2以考虑正确的象限
    azimuth = np.arctan2(y, x)    
    # 将方位角转换为度数，并确保范围在0到360度之间
    azimuth_degrees = np.degrees(azimuth)
    if azimuth_degrees < 0:
        azimuth_degrees += 360
    azimuth_degrees = 90-azimuth_degrees   
    if azimuth_degrees < 0:
        azimuth_degrees += 360    
    return azimuth_degrees
def calculate_jiajiao(a,b):#输出夹角0-180
    # 提取x和y分量
    angle = abs(a-b)
    if(angle>180):
        angle = 360-angle    
    return angle
def calculate_jiajiao2(a,b):#输出夹角0-360
    # 提取x和y分量
    if(b==360):
        b=0
    if(a<=b):
        angle = b-a
    else:
        angle = 360-(a-b)      
    return angle    