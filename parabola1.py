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
import sys
import numpy as np
import os
import cmocean
import statistics
from scipy.optimize import curve_fit
from pyproj import Transformer

if __name__=="__main__": 
    print ("开始",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    num_curves = 90
    colors = cmocean.cm.balance(np.linspace(0, 1, num_curves))  # 使用Viridis颜色映射
    for angle in range (10,80,10):
        add_Doppler_zero = [0 for x in range(48)]
        add_Doppler_zero  = np.array(add_Doppler_zero , dtype=np.float32) 
        add_Doppler = 0
        direction_s = 240#计算船舶方向参数  
        num_Doppler_zero = 0#累计个数
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
            if(np.max(current_ddm)<5000 and mix_direction>150 and infor_all[k][2]>angle and infor_all[k][2]<angle+10):
                Doppler_zero = [0 for x in range(48)]
                Doppler_zero = current_ddm[:,7]
                add_Doppler = add_Doppler + np.max(Doppler_zero)
                add_Doppler_zero = add_Doppler_zero + Doppler_zero/np.max(Doppler_zero)
                # add_Doppler_zero = add_Doppler_zero + Doppler_zero/10000
                num_Doppler_zero = num_Doppler_zero + 1
        add_Doppler_zero = add_Doppler_zero/num_Doppler_zero     
        print(add_Doppler/num_Doppler_zero)
        #按输出的最大值调整归一化比率
        plt.plot(np.linspace(-2, 3, 48), add_Doppler_zero*(add_Doppler/num_Doppler_zero/3560), color=colors[angle], alpha=0.7)

    plt.savefig('E:/1.5.2.png', dpi=512)
     
    print ("结束",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))


# 定义拟合函数，注意这里的x0是固定的
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