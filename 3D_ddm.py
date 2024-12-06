# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 18:55:42 2024

@author: kcy
"""

    
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import time


if __name__=="__main__":    
    
    print ("开始",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    
    # 生成数据
    x_ddm = np.linspace(-500, 500, 15)
    y_ddm = np.linspace(-2, 3, 48)
    x_ddm, y_ddm = np.meshgrid(x_ddm, y_ddm)
    # z_ddm = zoom(ddm, (1,2)) 
    z_ddm = ddm/np.max(ddm)
        # 创建图形对象
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # 绘制三维曲面图
    ax.plot_surface(x_ddm, y_ddm, z_ddm, cmap='viridis')
    
    # 设置坐标轴标签
    ax.set_xlabel('Doppler(Hz)')
    ax.set_ylabel('Delay(chip)')
    ax.set_zlabel('Z Label')
    
    # 显示图形
#    plt.show()
    plt.savefig('E:/1.5.0.png', dpi=512)