#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription:

from contextlib import closing

import aiofiles
import aiohttp
import asyncio
import os
import re
import requests
from datetime import datetime
# 加密解密模块
from Crypto.Cipher import AES
from selenium import webdriver
# 实现规避检测
from selenium.webdriver import ChromeOptions
# 无头浏览器设置(无可视化界面)
from selenium.webdriver.chrome.options import Options
from multiprocessing.dummy import Pool
from lxml import etree


def get_m3u8_from_re(url):
    """
    # 通过re获取m3u8文件下载路径
    :param url: 视频链接
    :return: m3u8文件的路径和名称
    """
    with closing(requests.get(url)) as response:
        src = re.findall('","url":"(.*?)","url_next"', response.text)[0]
        name = re.findall('class="data2">(.*?)</span>', response.text)[0]
        # 以'\'分割再拼接获取到m3u8的下载链接
        src = src.split("\\")
        src = ''.join(src)
        print(src, name)
        return src, name


def get_m3u8_from_selenium(url):
    """
    通过selenium获取ifram标签中的src属性中的m3u8文件下载路径
    :param url: 视频url
    :return:    m3u8文件的路径和名称
    """
    # 实现无可视化界面
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    # 实现规避检测
    option = ChromeOptions()
    option.add_experimental_option('useAutomationExtension', False)
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome('./documents/chromedriver',
                              chrome_options=chrome_options, options=option)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': 'Object.defineProperty(navigator,"webdriver",{get: () => undefined})'})

    driver.get(url)
    name = driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[1]/div[2]/h1/span').text
    src = driver.find_element_by_xpath('//*[@id="playleft"]/iframe').get_attribute('src')
    src = src.split('url=')[1]
    print(src, name)
    driver.quit()
    return src, name


def download_m3u8_file(src, name):
    """
    下载m3u8文件
    :param src:     下载m3u8文件对应的url
    :param name:    下载m3u8文件对应的存储路径及名称
    """
    with closing(requests.get(src)) as resp:
        with open(name, 'wb') as fp:
            fp.write(resp.content)
        print('m3u8文件下载完成')


# 通过读取第一个m3u8文件下载视频所对应的m3u8文件
def read_m3u8_file_first(src, first_name, second_name):
    """
    # 通过读取第一个m3u8文件下载视频所对应的m3u8文件
    :param src: 第一层m3u8文件下载url
    :param first_name:  第一层m3u8文件路径及名称
    :param second_name: 第二层m3u8文件存储路径及名称
    """
    domain_name = src.split('.cn')[0] + '.cn'   # 截取域名
    with open(first_name, 'r', encoding='utf-8') as fp:     # 通过第一层m3u8文件获取第二层m3u8文件
        for line in fp:
            if line.startswith('#'):
                continue
            else:
                line = line.strip()  # 去掉换行符和空白
                final_m3u8_url = domain_name + line
                print('m3u8最终链接:', final_m3u8_url)
                download_m3u8_file(final_m3u8_url, second_name)


def get_key(key_url):
    """
    请求m3u8文件中的链接获取解密所需的key值
    :param key_url: 解密所需key值的链接
    :return: key值
    """
    with closing(requests.get(key_url)) as resp:
        key = resp.text
        print(key)
        return key


async def download_ts_noAes(ts_url, ts_name, session):
    """
    下载非加密视频
    :param ts_url:  ts片段视频URL
    :param ts_name: ts片段视频存储名称
    :param session: 异步aiohttp提前创建的session
    """
    while True:
        try:
            async with session.get(ts_url) as response:
                async with aiofiles.open(ts_name, 'wb') as fp:
                    # 持久化存储未加密的ts视频
                    await fp.write(await response.content.read())
            print(ts_name + '下载完成')
            break
        except Exception as e:
            print(e)


async def download_ts_aes(ts_url, ts_name, session, key):
    """
    下载加密视频
    :param ts_url:  ts片段视频URL
    :param ts_name: ts片段视频存储名称
    :param session: 异步aiohttp提前创建的session
    :param key:     解密所需key值
    """
    aes = AES.new(key=key, IV=b'0000000000000000', mode=AES.MODE_CBC)
    while True:
        try:
            async with session.get(ts_url) as response:
                async with aiofiles.open(ts_name, 'wb') as fp:
                    # 请求ts视频url后获取到响应的二进制数据后先解密再持久化存储
                    bs = await response.content.read()
                    await fp.write(aes.decrypt(bs))
            print(ts_name + '下载完成')
            break
        except Exception as e:
            print(e)


async def aio_dowmload_video(m3u8_name, path_video):
    """
    创建异步视频下载任务
    :param m3u8_name: 包含ts视频文件url的m3u8文件名
    :param path_video:ts视频文件存储路径
    """
    tasks = []
    name_num = 1
    key = ''
    # 提前创建session，以防每次下载请求都重新创建
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with aiofiles.open(m3u8_name, mode='r', encoding='utf-8') as fp:
            async for line in fp:
                # 对m3u8文件中含有不止一个加密key时的处理
                line = line.strip()
                if line.startswith('#'):
                    if line.endswith('key"'):
                        key_url = re.findall('URI="(.*?)"', line)[0]
                        key = get_key(key_url)
                        continue
                    else:
                        continue
                else:
                    video_name = path_video + str(name_num) + '.ts'     # ts视频存储路径及名称
                    # 对加密的视频和非加密的视频区别处理
                    # 创建异步任务并传入提前创建的session
                    if key == '':
                        task = asyncio.create_task(download_ts_noAes(line, video_name, session))
                    else:
                        task = asyncio.create_task(download_ts_aes(line, video_name, session, key))
                    tasks.append(task)
                    name_num += 1
            await asyncio.wait(tasks)  # 等待任务结束


def merge_ts(path, name):
    """
    ts视频合并
    :param name:
    :param path:    ts视频保存文件夹路径
    """
    ts_sorted_list = []
    s = ''
    s_ffmpeg = ''
    if os.path.isdir(path):
        ts_list = os.listdir(path)
        for ts in ts_list:
            if '.ts' not in ts:
                del ts
            else:
                t = int(ts.split('.ts')[0])
                ts_sorted_list.append(t)
    for i in sorted(ts_sorted_list):
        s = s + str(i) + '.ts '
        s_ffmpeg = s_ffmpeg + str(i) + '.ts|'
    # 切换工作目录到ts视频文件所在
    # os.chdir('./documents/video/')
    os.chdir(path)
    # cat命令合成视频
    # os.system('cat {} > {}.mp4'.format(s,name))
    # ffmpeg命令合并视频
    os.system('ffmpeg -i "concat:{}" -acodec copy -vcodec copy -absf aac_adtstoasc {}.mp4'.format(s_ffmpeg, name))

    # 合并完成后移除所有ts视频文件
    for i in ts_sorted_list:
        if os.path.exists(str(i)+'.ts'):
            os.remove(str(i)+'.ts')


def star_download(url):
    """
    主函数
    """
    # url = 'https://www.pianba.net/yun/25456-2-1.html'
    m3u8_src, m3u8_name = get_m3u8_from_re(url)
    path_m3u8 = './documents/m3u8文件/'
    path_video = './documents/video/{}/'.format(m3u8_name)
    if not os.path.isdir(path_video):
        os.mkdir(path_video)
    m3u8_name_first = path_m3u8 + m3u8_name + '_first.txt'
    m3u8_name_second = path_m3u8 + m3u8_name + '_second.txt'
    download_m3u8_file(m3u8_src, m3u8_name_first)    # 下载第一个m3u8文件
    read_m3u8_file_first(m3u8_src, m3u8_name_first, m3u8_name_second)     # 下载最终m3u8文件
    asyncio.run(aio_dowmload_video(m3u8_name_second, path_video))  # 异步执行下载视频
    # 在获取到二进制响应数据后先解密再持久化存储时可以不用
    # asyncio.run(aio_dec(key,path_video))
    merge_ts(path_video, m3u8_name)      # 合成视频


def main():
    url_main = input('请输入要下载的视频链接：')
    url_list = []
    with closing(requests.get(url_main)) as resp:
        tree = etree.HTML(resp.text)
        li_list = tree.xpath('/html/body/div[1]/div/div/div/div/div[2]/ul/li')
        for li in li_list:
            url = 'https://www.pianba.net/' + li.xpath('.//a/@href')[0]
            url_list.append(url)
    # print(url_list)
    pool = Pool(4)
    pool.map(star_download, url_list)
    pool.close()
    pool.join()


if __name__ == '__main__':
    starTime = datetime.now()
    main()
    # star_download('https://www.pianba.net/yun/25456-2-2.html')
    endTime = datetime.now()
    print('下载完成，耗时：', endTime - starTime)
