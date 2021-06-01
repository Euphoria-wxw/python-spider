#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription:

# 1.按行读取music.txt文件提取下载歌曲名称
# 2.根据文本中的歌名查找歌曲获取歌曲id  https://music.163.com/weapi/search/suggest/web
# https://music.163.com/weapi/cloudsearch/get/web
# 歌曲id: result['songs'][0]['id']
# 3.根据id请求歌曲  https://music.163.com/weapi/song/enhance/player/url/v1
# 歌曲下载链接：data[0]['url]
# 4.请求歌曲下载链接持久化存储歌曲

from enc_wangyiyun import get_params,get_encSecKey
from datetime import datetime
import aiofiles
import aiohttp
import asyncio
import json
import difflib  # 比较两个字符串相似度

data_search = {
    'csrf_token': "",
    'hlposttag': '</span>',
    'hlpretag': '<span class=\"s-fc7\">',
    'limit': "30",
    'offset': "0",
    's': "沦陷-李学仕",
    'total': "true",
    'type': "1"
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'origin': 'https://music.163.com',
    'referer': 'https://music.163.com/search/'
}
url_search = 'https://music.163.com/weapi/cloudsearch/get/web'
url_download = 'https://music.163.com/weapi/song/enhance/player/url/v1'
music_id_all = []

async def get_music_id(session, line):
    """
    获取歌曲id
    :param session:
    :param line:
    """
    data = {
        # 默认传入的data是字符串类型
        'params': get_params(json.dumps(data_search)),
        'encSecKey': get_encSecKey()
    }
    author_name = line.split('-')[1]  # 作者名
    music_name = line.split('-')[0]  # 歌名
    flag = True
    # while True:
    try:
        async with session.post(url_search, data=data) as resp:
            resp_json = await resp.json(content_type='text/plain', encoding='utf-8')
            songs = resp_json['result']['songs']
            for song in songs:
                ar_name = song['ar'][0]['name']
                al_name = song['name']
                # print(music_name + '-' + al_name)
                # print(al_name + '-' + ar_name)
                # 用作者名和歌名相似度匹配筛选正确的歌曲
                if (difflib.SequenceMatcher(None, author_name, ar_name).quick_ratio() > 0.9
                        and difflib.SequenceMatcher(None, music_name, al_name).quick_ratio() > 0.9
                        # 筛选过滤掉vip歌曲
                        and (song['rt'] is None or song['rt'] == '')):
                    music_id = song['id']
                    flag = False
                    # 异步获取歌曲id存成列表
                    dict = {
                        'id': music_id,
                        'name': al_name + '-' + ar_name
                    }
                    music_id_all.append(dict)
                    # print(music_id)
                    # get_music_url(music_id,ar_name,al_name)
                else:
                    continue
            if flag:    # 找不到匹配的歌曲
                print('歌曲：{},作者：{} 未找到或无版权'.format(music_name,author_name))
        #     break
    except Exception as e:
        print(al_name + '-' + ar_name,'下载失败')
        print(e)


async def get_download_music_name(music):
    """
    根据music.txt文件获取歌曲id
    :param music: 批量下载歌曲文件
    """
    tasks = []
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),headers=headers) as session:
        async with aiofiles.open(music, mode='r', encoding='utf-8') as fp:
            async for line in fp:
                line = line.strip()  # 去空格
                if line.startswith('#'):
                    continue
                elif line.find('-') == -1:
                    print(line + '格式错误,请重新录入')
                    continue
                else:
                    data_search['s'] = line
                    task = asyncio.create_task(get_music_id(session, line))
                    tasks.append(task)
            await asyncio.wait(tasks)


async def get_music_url():
    """
    根据id获取歌曲下载链接
    :param id:  歌曲id
    :param al_name: 歌名
    :param ar_name: 作者名
    """
    tasks = []
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        for dict in music_id_all:
            data_download = {
                'csrf_token': "",
                'encodeType': "aac",
                'ids': "[{}]".format(dict['id']),
                'level': "standard"
            }
            data = {
                # 默认传入的data是字符串类型
                'params': get_params(json.dumps(data_download)),
                'encSecKey': get_encSecKey()
            }
            async with session.post(url_download, data=data) as resp:
                resp.encoding = 'utf-8'
                res_json = await resp.json(content_type='text/plain', encoding='utf-8')
                url_music = res_json['data'][0]['url']
                # print(url_music)
                task = asyncio.create_task(download_music(session,url_music, dict))
                tasks.append(task)
        await asyncio.wait(tasks)


async def download_music(session, url,dict):
    """
    持久化存储歌曲
    :param url: 歌曲下载链接
    :param al_name: 歌名
    :param ar_name: 作者名
    """
    name = dict['name'] + '.mp3'
    # print(url)
    async with session.get(url) as resp:
        content = await resp.content.read()
        if content:
            print('开始下载：',name)
            async with aiofiles.open('music/' + name, mode='wb') as fp:
                await fp.write(content)
            print(name + '下载完成')
        else:
            print(name + '下载失败')


def main():
    """
    主函数
    """
    asyncio.run(get_download_music_name('music.txt'))
    asyncio.run(get_music_url())


if __name__ == '__main__':
    starTime = datetime.now()
    main()
    endTime = datetime.now()
    print('下载完成，耗时：', endTime - starTime)