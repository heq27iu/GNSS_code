# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 13:22:24 2024

@author: kcy
"""

from mpl_toolkits.basemap import Basemap
map = Basemap(llcrnrlon = 0, llcrnrlat = -90, urcrnrlon = 360, urcrnrlat = 90,resolution = 'l')
#map = Basemap(llcrnrlon = 100, llcrnrlat = 0, urcrnrlon = 180, urcrnrlat = 60,resolution = 'l')
import matplotlib as mpl
import matplotlib.pyplot as plt 
from scipy import interpolate
from scipy.interpolate import interp1d
import math
from scipy import misc
import netCDF4 as nc
import time
import sys
import numpy as np
import os
import cmocean
from multiprocessing import Pool
from scipy.ndimage import filters
from scipy.ndimage import morphology
from pyproj import Transformer

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

if __name__=="__main__": 
    print ("开始",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    #参数设置
    angle_axis = 72#角度分辨率
    rader = [[0 for x in range(32)]  for x in range(angle_axis)] 
    rader = np.array(rader, dtype=np.float32) 
    ave_rader = [[0 for x in range(1)]  for x in range(angle_axis)] 
    ave_rader_line = [0 for x in range(angle_axis)]
    # ave_rader = np.array(ave_rader, dtype=np.float32) 
    direction_s = 240#计算船舶方向参数
    for i in range (int(len(infor_all)*0.15),int(len(infor_all)*0.9),1):
        if(infor_all[i][2]>50 and infor_all[i][2]<65 and pos_all[int(i/4)][4]>0):
            ship_direction = calculate_azimuth(np.array([(infor_all[i+direction_s][8]-infor_all[i][8]), (infor_all[i+direction_s][7]-infor_all[i][7]),]))
            if(ship_direction>90):
                antenna_direction = ship_direction-90
            else:
                antenna_direction = ship_direction+270         
            mix_direction = calculate_jiajiao2(infor_all[i][3],antenna_direction)
            ddm_max = np.max(ddm_all[i])
            ave_rader[int(mix_direction/int(360/angle_axis))].append(ddm_max)
            if(ddm_max >= 16000):
                ddm_max = 15999      
            
            
            #rader[int(infor_all[i][3]/int(360/angle_axis))][int(ddm_max/500)] = rader[int(infor_all[i][3]/int(360/angle_axis))][int(ddm_max/500)] + 1
            rader[int(mix_direction/int(360/angle_axis))][int(ddm_max/500)] = rader[int(mix_direction/int(360/angle_axis))][int(ddm_max/500)] + 1
        
    # rader[rader > 20000] = 20000
    log_rader = np.log2(rader + 1)#取对数
    for j in range (0,angle_axis,1):       
        ave_rader_line[j] = np.sum(ave_rader[j])/(len(ave_rader[j])-1)  
    ave_rader_line[j] = ave_rader_line[0]
    # 创建数据
    theta = np.linspace(0, 2 * np.pi, angle_axis)  # 角度，从0到2π
    yheta = np.linspace(0, 16, 32)
    r = np.linspace(0, 1, angle_axis) 
    for j in range (0,angle_axis,1):  
        r[j] = ave_rader_line[j]/500
    f_cubic = interp1d(theta, r, kind='cubic')
    r_cubic = f_cubic(theta)
    # 创建极坐标图
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N') 
    ax.set_theta_direction(-1) 
    # 绘制图像
    njet = cmocean.cm.balance  
    ax.pcolormesh(theta,yheta,log_rader.T,linewidth=0,cmap=njet)   #画出频率分布图 (横坐标、纵坐标、频率值、网格线颜色、网格颜色、透明度)
    ax.plot(theta, r_cubic,)
    ax.set_ylim(0, 16)
    ax.set_yticks([2, 4, 6, 8, 10, 12, 14])
    ax.set_yticklabels([' ', ' ', ' ', ' ', ' ', ' ', ' '])
    #ax.imshow(rader.T,cmap=cmocean.cm.balance,interpolation='bicubic',extent=(0,2*np.pi,0,10000))
    plt.savefig('E:/2_11', dpi=512)
    print ("结束",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))