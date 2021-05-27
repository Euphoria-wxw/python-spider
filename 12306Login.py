#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription:

import base64
from chaojiying import Chaojiying_Client
from selenium import webdriver
# 实现规避检测
from selenium.webdriver import ChromeOptions
# 动作链操作
from selenium.webdriver import ActionChains
from lxml import etree
from time import sleep


# 获取验证码图片
def get_loginImg(html):
    tree = etree.HTML(html)
    img_src = tree.xpath('//*[@id="J-loginImg"]/@src')[0]
    img_src = img_src.replace('data:image/jpg;base64,','')
    # data:image/jpg;base64格式转换为图片
    page_content = base64.b64decode(img_src)
    with open('./a.jpeg','wb') as fp:
        fp.write(page_content)


# 通过调用超级鹰识别验证码并返回坐标
def get_chaojiying():
    chaojiying = Chaojiying_Client('超级鹰用户名', '密码', 'ID')    # 用户中心>>软件ID 生成一个替换 96001
    im = open('./a.jpeg', 'rb').read()  # 本地图片文件路径 来替换 a.jpeg
    # print(chaojiying.PostPic(im, 9004))  # 1902 验证码类型 官方网站>>价格体系
    result = chaojiying.PostPic(im, 9004)['pic_str']
    print(result)  # 1902 验证码类型 官方网站>>价格体系

    # 验证码坐标
    offset_list = []
    result_list = result.split('|')     # 以'|'分割每个需点击的位置坐标
    for offset in result_list:
        offset_list.append(offset.split(','))   # 以','分割x,y坐标
    return offset_list


def main():
    # 关闭“chrome正受到自动测试软件的控制”
    option = ChromeOptions()
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_experimental_option('useAutomationExtension', False)
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 不自动关闭浏览器
    option.add_experimental_option("detach", True)

    driver.get('https://www.12306.cn/index/')

    try:
        # 点击登录
        driver.find_element_by_xpath('//*[@id="J-header-login"]/a[1]').click()
        sleep(1)
        # 点击账号登录
        driver.find_element_by_xpath('/html/body/div[2]/div[2]/ul/li[2]/a').click()

        username_tag = driver.find_element_by_id('J-userName')      # 获取用户名所在标签
        password_tag = driver.find_element_by_id('J-password')      # 获取密码所在标签
        loginImg_tag = driver.find_element_by_xpath('//*[@id="J-loginImg"]')    # 获取验证码图片所在标签
        loginButton_tag = driver.find_element_by_id('J-login')      # 获取登录按钮所在标签

        username_tag.send_keys('xxx')     # 输入用户名
        password_tag.send_keys('xxx')       # 输入密码

        # 获取12306验证码图片
        get_loginImg(driver.page_source)
        # 通过调用超级鹰识别验证码并返回坐标
        offset_list = get_chaojiying()

        for offset in offset_list:
            # 执行动作链事件
            ActionChains(driver).move_to_element_with_offset(loginImg_tag,int(offset[0]),int(offset[1])).click().perform()
        sleep(1)
        # 点击立即登录按钮
        loginButton_tag.click()
        sleep(1)
        loginSlide_tag = driver.find_element_by_xpath('//*[@id="nc_1_n1z"]')  # 滑块所在标签
        action = ActionChains(driver)       # 创建动作链
        action.click_and_hold(loginSlide_tag)       # 点击长按指定的标签
        action.move_by_offset(300,0).perform()    # 拖动的坐标
        action.release()        # 释放动作链

    finally:
        # 延迟10秒后关闭浏览器
        sleep(10)
        driver.quit()


if __name__ == '__main__':
    main()