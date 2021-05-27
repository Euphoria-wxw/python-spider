#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription:

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver import ActionChains
import time, requests
from lxml import etree
import slideUnlock


class Qzone(object):
    def __init__(self,username,password):
        option = ChromeOptions()
        option.add_argument('--disable-blink-features=AutomationControlled')
        option.add_experimental_option('useAutomationExtension', False)
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 不自动关闭浏览器
        option.add_experimental_option("detach", True)
        self.url = 'https://qzone.qq.com/'
        self.driver = webdriver.Chrome('./chromedriver',options=option)
        self.username = username
        self.password = password

    # 获取缺口背景图
    def get_slideBg(self,tree):
        # slideBg = self.driver.find_element_by_id('slideBg')
        # slideBg.screenshot('slideBg.png')

        img_src = tree.xpath('//*[@id="slideBg"]/@src')[0]
        url = 'https://t.captcha.qq.com' + img_src
        res = requests.get(url)
        with open('slideBg.png', 'wb') as fp:
            fp.write(res.content)

    # 获取缺口图片
    def get_slideBlock(self,tree):
        img_src = tree.xpath('//*[@id="slideBlock"]/@src')[0]
        url = 'https://t.captcha.qq.com' + img_src
        res = requests.get(url)
        with open('slideBlock.png', 'wb') as fp:
            fp.write(res.content)

    def start_login(self):
        """
        登录
        """
        self.driver.get(self.url)
        try:
            time.sleep(1)
            tcaptcha = self.driver.find_element_by_id("login_frame")
            self.driver.switch_to.frame(tcaptcha)
            self.driver.find_element_by_xpath('//*[@id="switcher_plogin"]').click()
            self.driver.find_element_by_id('u').send_keys(self.username)
            self.driver.find_element_by_id('p').send_keys(self.password)
            time.sleep(1)
            # 点击登录
            self.driver.find_element_by_id('login_button').click()
            time.sleep(2)
            # 切换iframe
            self.driver.switch_to.frame(self.driver.find_element_by_id("tcaptcha_iframe"))
            # 切换完获取网页源代码
            tree = etree.HTML(self.driver.page_source)
            self.get_slideBg(tree)
            self.get_slideBlock(tree)

            # 滑块及缺口背景图路径
            slideBg_path = "slideBg.png"
            slideBlock_path = "slideBlock.png"

            # 获取滑块需移动的距离
            slide = slideUnlock.Slide(slideBg_path, slideBlock_path)
            left = slide.get_element_slide_distance()

            # qq空间下载缺口背景图存在缩放，且滑块初始距离为22，如下计算真实移动距离
            real_left = left * 280 / 680 - 22
            print('实际移动距离：',real_left)
            # 获取滑块所在标签
            div = self.driver.find_element_by_xpath('//*[@id="tcaptcha_drag_thumb"]')

            # 利用加速度模拟轨迹移动(推荐)
            # 获取移动轨迹
            track = slide.get_track(real_left)
            # 点击长按滑块标签
            ActionChains(self.driver).click_and_hold(div).perform()
            # 移动滑块
            for i in track:
                ActionChains(self.driver).move_by_offset(xoffset=i,yoffset=0).perform()
            # 释放动作链
            ActionChains(self.driver).release().perform()

            # 一次性直接移动滑块(不推荐)
            # ActionChains(self.driver).drag_and_drop_by_offset(div, xoffset=real_left, yoffset=0).perform()
        finally:
            time.sleep(10)
            self.driver.quit()


def main():
    username = '123456@qq.com'
    password = '123456'
    qzone = Qzone(username,password)
    qzone.start_login()


if __name__ == '__main__':
    main()