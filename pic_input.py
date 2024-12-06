# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 16:30:04 2024

@author: kcy
"""

from mpl_toolkits.basemap import Basemap
map = Basemap(llcrnrlon = 0, llcrnrlat = -90, urcrnrlon = 360, urcrnrlat = 90,resolution = 'l')
#map = Basemap(llcrnrlon = 100, llcrnrlat = 0, urcrnrlon = 180, urcrnrlat = 60,resolution = 'l')
import matplotlib as mpl
import matplotlib.pyplot as plt 
from scipy import interpolate
from scipy import misc
import netCDF4 as nc
import time
import sys
import numpy as np
import os
from tqdm import tqdm  # 导入 tqdm 进度条库
from multiprocessing import Pool
from scipy.ndimage import filters
from scipy.ndimage import morphology
from pyproj import Transformer
from PIL import Image
from scipy.ndimage import zoom
import csv

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

def delete_all_files_in_directory(directory_path):
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在。")
        return

    # 遍历目录中的所有文件和子目录
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # 如果是文件，则删除
        if os.path.isfile(file_path):
            os.remove(file_path)
            # print(f"已删除文件: {file_path}")

def writeimg():
    #计算海浪插值结果
    for i in tqdm(range(0,len(pos_all),1), desc="Processing Images"):       
        time_hour = pos_all[i][3]/60#把时间换算成小时
        time_hour_int = int(time_hour)
        if(pos_all[i][1]>180):
            pos_all[i][1] = pos_all[i][1]-180
        else:
            pos_all[i][1] = pos_all[i][1]+180
        pos_all[i][4] = interpolator0([time_hour,pos_all[i][0],pos_all[i][1]])
    #计算海浪插值结果完结
    directory_path = 'E:/GNSS-R_wave/ddm/'  # 将此路径替换为你的目标目录路径
    delete_all_files_in_directory(directory_path) # 清空原文件
    data = []# 要写入 CSV 文件的数据
    data_wave_value = ["filename","value","angle","direction"]
    data.append(data_wave_value)
    direction_s = 240#计算船舶方向参数
    for i in tqdm(range(0,len(infor_all),1), desc="Processing Images"):       
        ddm = ddm_all[i] 
        ddm_front = ddm_front_all[i]         
        ddm_front_front = ddm_front_front_all[i]         
        if( i > len(infor_all)*0.15 and i < len(infor_all)*0.9 and infor_all[i][10] < 0.1 and np.max(ddm)<25000 and pos_all[int(i/4)][4]!=0 and infor_all[i][2]>40 and infor_all[i][2]<50):             
            ddm_area = 120

            ddm = ddm/ddm_area            
            ddm = zoom(ddm, zoom_factor) 
            ddm_front = ddm_front/ddm_area            
            ddm_front = zoom(ddm_front, zoom_factor)            
            ddm_front_front = ddm_front_front/ddm_area            
            ddm_front_front = zoom(ddm_front_front, zoom_factor)          
            
            ddm = np.stack((ddm, ddm_front, ddm_front_front), axis=2)                                  
            ddm = ddm.astype(np.uint8)  # 转换为无符号8位整数

            
            #计算真实方向角
            ship_direction = calculate_azimuth(np.array([(infor_all[i+direction_s][8]-infor_all[i][8]), (infor_all[i+direction_s][7]-infor_all[i][7]),]))
            if(ship_direction>90):
                antenna_direction = ship_direction-90
            else:
                antenna_direction = ship_direction+270         
            mix_direction = calculate_jiajiao2(infor_all[i][3],antenna_direction)
            
            
            if(mix_direction<30):
                # 将数组转换为图像
                image = Image.fromarray(ddm)
                # 保存为JPEG格式
                image.save('E:/GNSS-R_wave/ddm/'+str(i)+'.jpg')
                
                data_wave_value = [str(i),pos_all[int(i/4)][4],infor_all[i][2],mix_direction]
                data.append(data_wave_value)
        
    csv_file_path = 'E:/GNSS-R_wave/ddm.csv'# 指定 CSV 文件的路径
    # 写入 CSV 文件
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)   
        writer.writerows(data)# 写入数据
    print(f"数据已成功写入 {csv_file_path}")


if __name__=="__main__": 
    print ("开始",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))   
    
    cha_num = 4;            #反射通道数
    corr_num = 48;          #相关路数（I/Q)
    freq_band = 15;         #频段数
    subframelen = 738;      #子帧长
    zoom_factor = (1,3)  # 例如，将数组大小扩大2倍
     
    data = np.fromfile("E:/GNSS-R_wave/data/BD2B1_RefSigFile[2023-04-11 18.09.19].dat", dtype=np.uint16)
    tip = cha_num*subframelen;
    infor_all = [];
    ddm_all = [];
    ddm_front_all = [];
    ddm_front_front_all = [];
    pos_all = [];
    # 创建转换器
    transformer_to_geodetic = Transformer.from_crs("epsg:4978", "epsg:4326")
    transformer_to_ecef = Transformer.from_crs("epsg:4326", "epsg:4978")

    time_0_max = int(len(data)/tip)


    #读取数据
    wavedataall = []
    for root, dirs, files in os.walk("E:/GNSS-R_wave/data/wave/"):
        for file in files:
            file_path = os.path.join(root, file)
            # 处理文件路径
            file = nc.Dataset(file_path)
            #data_wave = file['VHM0'][:]#有效波高
            data_wave = file['VHM0_WW'][:]#风浪
            data_wave = np.array(data_wave, dtype=np.float32)
            data_wave = np.where(data_wave < 0, 0, data_wave)
            for i in range(0,4,1):
                wavedataall.append(data_wave[i])
    wavedataall = np.array(wavedataall, dtype=np.float32)    
    #读取数据完毕
    print ("读取数据结束",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    
    lon = np.linspace(0,360,4320) 
    lat = np.linspace(-90,90,2041)
    time_arry = np.linspace(0,1944,648)
    interpolator0 = interpolate.RegularGridInterpolator((time_arry,lat,lon), wavedataall, method='linear')
    
    # windin = [[0 for x in range(180)]for x in range(360)]
    # windin = np.array(windin, dtype=np.float32)  
    # for tlat in range (-90,90,1):
    #     for tlon in range (0,360,1):
    #         windin[tlon][tlat] = interpolator0([2,tlat,tlon])
            
    
    for time_0 in tqdm(range(0,time_0_max-2,120), desc="Processing Images"):          
        pos = [0 for x in range(5)]
        pos = np.array(pos, dtype=np.float32) 
        for cha in range (0,4,1):
            infor = [0 for x in range(12)]
            infor = np.array(infor, dtype=np.float32)  
            ddm = [[0 for x in range(15)]for x in range(48)]
            ddm = np.array(ddm, dtype=np.float32)  
            ddm_front = [[0 for x in range(15)]for x in range(48)]
            ddm_front = np.array(ddm_front, dtype=np.float32)  
            ddm_front_front = [[0 for x in range(15)]for x in range(48)]
            ddm_front_front = np.array(ddm_front_front, dtype=np.float32)  
            infor[0] = data[time_0*tip+cha*subframelen+4]
            infor[1] = data[time_0*tip+cha*subframelen+5]
            infor[2] = data[time_0*tip+cha*subframelen+6]/10
            infor[3] = data[time_0*tip+cha*subframelen+7]/10
            infor[4] = ((np.int32(data[time_0*tip+cha*subframelen+9])<<16)+int(data[time_0*tip+cha*subframelen+8]))/10
            infor[5] = ((np.int32(data[time_0*tip+cha*subframelen+11])<<16)+int(data[time_0*tip+cha*subframelen+10]))/10
            infor[6] = ((np.int32(data[time_0*tip+cha*subframelen+13])<<16)+int(data[time_0*tip+cha*subframelen+12]))/10
            latitude, longitude, altitude = transformer_to_geodetic.transform(infor[4], infor[5], infor[6])
            infor[7] = latitude
            infor[8] = longitude
            infor[9] = altitude
            
            for cha_0_y in range (0,15,1):
                for cha_0_x in range (0,48,1):
                    ddm[cha_0_x][cha_0_y] = int(data[time_0*tip+cha*subframelen+cha_0_y*48+cha_0_x+14])
                    # if(ddm[cha_0_x][cha_0_y]>250):
                    #     ddm[cha_0_x][cha_0_y]=250        
            ddm_all.append(ddm)   
            for cha_0_y in range (0,15,1):
                for cha_0_x in range (0,48,1):
                    ddm_front[cha_0_x][cha_0_y] = int(data[(time_0+1)*tip+cha*subframelen+cha_0_y*48+cha_0_x+14])
            ddm_front_all.append(ddm_front)  
            for cha_0_y in range (0,15,1):
                for cha_0_x in range (0,48,1):
                    ddm_front_front[cha_0_x][cha_0_y] = int(data[(time_0+2)*tip+cha*subframelen+cha_0_y*48+cha_0_x+14])
            ddm_front_front_all.append(ddm_front_front) 
            infor[10] = abs(np.max(ddm)-np.max(ddm_front))/np.max(ddm)#判断是否为噪声根据最大值
            infor_all.append(infor)
        pos[0] = infor[7]
        if(infor[8]>0):
            pos[1] = infor[8]
        else:
            pos[1] = 360 + infor[8]
        pos[2] = infor[9]
        pos[3] = 1089.3 + time_0/60 #时间的分钟数，1089.3对应当天的起始时间的分钟
        pos_all.append(pos)
    pos_all = np.array(pos_all, dtype=np.float32) 
    print ("原始数据处理结束",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    writeimg()
    
    del wavedataall
    print ("结束",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        
        
        