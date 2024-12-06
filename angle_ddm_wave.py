# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 13:56:44 2024

@author: kcy
"""


from mpl_toolkits.basemap import Basemap
map = Basemap(llcrnrlon = 0, llcrnrlat = -90, urcrnrlon = 360, urcrnrlat = 90,resolution = 'l')
#map = Basemap(llcrnrlon = 100, llcrnrlat = 0, urcrnrlon = 180, urcrnrlat = 60,resolution = 'l')
import matplotlib as mpl
import matplotlib.pyplot as plt 
from scipy import interpolate
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

def calculate_jiajiao(a,b):#输出夹角
    # 提取x和y分量
    angle = abs(a-b)
    if(angle>180):
        angle = 360-angle    
    return angle

if __name__=="__main__": 
    print ("开始",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    for anrange in range(42,80,100):
        ddm_angle_wave_infor = []
        ddm_sun_infor = []
        ddm_line = [[0 for x in range(1)]  for x in range(6)] 
        # angel_infor = np.array(angel_infor, dtype=np.float32) 
        #for i in range (0,len(infor_all)-100,4):
        for i in range (int(len(infor_all)*0.14),int(len(infor_all)*0.9),4):
            # angel_num = infor_all[i][1]    
            ship_direction = calculate_azimuth(np.array([(infor_all[i+20][8]-infor_all[i][8]), (infor_all[i+20][7]-infor_all[i][7]),]))
            if(ship_direction>90):
                antenna_direction = ship_direction-90
            else:
                antenna_direction = ship_direction+270
            ddm_angle_wave = [int(i/4),0,0,0,ship_direction]
            ddm_angle_wave[1] = infor_all[i][2]
            if(ddm_angle_wave[1]>65):
                ddm_angle_wave[2] = (np.max(ddm_all[i]))/(1-(ddm_angle_wave[1]-65)/50)
            else:
                ddm_angle_wave[2] = (np.max(ddm_all[i]))/(1-(65-ddm_angle_wave[1])/120)
            ddm_angle_wave[3] = pos_all[int(i/4),4]
            ddm_angle_wave_infor.append(ddm_angle_wave)
            if(infor_all[i][10] < 0.1 and ddm_angle_wave[3]>0 and ddm_angle_wave[3]<6 and ddm_angle_wave[1]>=anrange and ddm_angle_wave[1]<anrange+10 and ddm_angle_wave[2]>0 and ddm_angle_wave[2]<50000 and calculate_jiajiao(infor_all[i][3],antenna_direction)<30):
                ddm_line[int(ddm_angle_wave[3]*1)].append(np.max(ddm_all[i]))
                
                ddm_sun_infor.append([ddm_angle_wave[2],ddm_angle_wave[3]])
                # ddm_sun_infor.append([np.max(ddm_all[i]),ddm_angle_wave[3]])
                
        ddm_angle_wave_infor = np.array(ddm_angle_wave_infor, dtype=np.float32) 
        ddm_sun_infor = np.array(ddm_sun_infor, dtype=np.float32) 
    
        ddm_line_ave = [0 for x in range(6)]  
        for i in range (0,len(ddm_line_ave),1):
            if(len(ddm_line[i])>1):
               ddm_line_ave[i] = np.sum(ddm_line[i])/(len(ddm_line[i])-1)
            else:
               ddm_line_ave[i] = 0
    
        coefficients = np.polyfit(ddm_sun_infor[:,1], ddm_sun_infor[:,0], 1)
        slope, intercept = coefficients
        correlation_matrix = np.corrcoef(ddm_sun_infor[:,1], ddm_sun_infor[:,0])
        print(anrange,slope,correlation_matrix[0, 1])
        y_fit = slope * ddm_sun_infor[:,1] + intercept
        
        plt.plot(ddm_sun_infor[:,1], y_fit, color='red', alpha=0.7,label=f'拟合直线: y={slope:.2f}x+{intercept:.2f}')
        
        plt.scatter(ddm_sun_infor[:,1], ddm_sun_infor[:,0], color='blue',alpha=0.1,edgecolors='none',s=25)
        #X = np.linspace(0,6,6) 
        #plt.plot(X,ddm_line_ave, color='green', linestyle='-', linewidth=2, label='Line 1')
        # plt.title('angle_value_line')
        plt.savefig('E:/3.6.png', dpi=512)
    
    print ("结束",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    
        
        
        