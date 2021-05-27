#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription:

import cv2
import numpy as np


class Slide(object):
    """
    根据滑块图片，获取缺口背景图中缺口所在坐标，
    即滑块图片所需移动距离
    :param slideBg_path: 缺口背景图保存路径
    :param  slideBlock_path: 滑块图片保存路径
    """
    def __init__(self, slideBg_path, slideBlock_path):
        self.slideBg_path = slideBg_path
        self.slideBlock_path = slideBlock_path

    def get_element_slide_distance(self):
        """
        计算
        :return: 滑块所需移动距离
        """
        # 读取1通道缺口滑块图片
        slideBlock = cv2.imread(self.slideBlock_path, 0)
        # 获取缺口图数组的形状 -->缺口图的宽和高
        width, height = slideBlock.shape[::-1]
        # 另存为
        slideBlockNew = 'slideBlockNew.png'
        cv2.imwrite(slideBlockNew, slideBlock)
        # 读取另存的缺口滑块图
        slideBlock_gray = cv2.imread(slideBlockNew)
        # 进行色彩转换,转换成灰度图
        slideBlock_gray = cv2.cvtColor(slideBlock_gray, cv2.COLOR_BGR2GRAY)
        # 获取色差的绝对值
        slideBlock_gray = abs(255 - slideBlock_gray)
        # 保存灰度滑块图
        cv2.imwrite(slideBlockNew, slideBlock_gray)
        # 读取灰度滑块图
        slideBlock_gray = cv2.imread(slideBlockNew)

        # 缺口背景图
        slideBg_rgb = cv2.imread(self.slideBg_path)
        slideBg_rgb = cv2.cvtColor(slideBg_rgb, cv2.COLOR_BGR2GRAY)
        slideBgNew = 'slideBgNew.png'
        cv2.imwrite(slideBgNew, slideBg_rgb)
        slideBg_gray = cv2.imread(slideBgNew)
        # 对两张图片进行对比
        res = cv2.matchTemplate(slideBlock_gray, slideBg_gray, cv2.TM_CCOEFF_NORMED)
        top, left = np.unravel_index(np.argmax(res), res.shape)  # 通过np转化为数值，就是坐标
        print("当前滑块的缺口位置：", (left, top, left + width, top + height))
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance:偏移量
        :return:移动轨迹
        """
        track = []      # 移动轨迹
        current = 0     # 当前位移
        mid = distance * 4 / 5  # 减速阈值  362.4
        t = 1     # 计算间隔
        v = 0       # 初速度

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 8
            else:
                # 加速度为负3
                a = -5
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + (1/2 * a * t * t)
            # 当前位移
            current += move
            # 最后一段轨迹处理
            if current > distance:
                move = distance-(current-move)
            # 加入轨迹
            track.append(round(move))
        print('移动轨迹：', track)
        return track

def test():
    slideBg_path = "QzoneLogin/slideBg.png"
    slideBlock_path = "QzoneLogin/slideBlock.png"
    slide = Slide(slideBg_path, slideBlock_path)
    y = slide.get_element_slide_distance()

    track = slide.get_track(y)
    sum = 0
    for i in track:
        sum+=i
    print(sum)

if __name__ == '__main__':
    test()
