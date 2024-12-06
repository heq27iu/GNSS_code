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
    z_ddm = zoom(ddm, (1,3)) 
    z_ddm = z_ddm/np.max(z_ddm)
        # 创建图形对象
    fig = plt.figure()
    # 绘制二维曲面图
    plt.imshow(z_ddm, cmap='viridis', interpolation='none', extent=[0, 45, 0, 48])
    
    # plt.xlim(-500, 500)  # x轴范围从0到2
    # plt.ylim(-2, 3)  # y轴范围从0到2
    
    # 显示图形
#    plt.show()
    plt.savefig('E:/1.5.1.5.png', dpi=512)