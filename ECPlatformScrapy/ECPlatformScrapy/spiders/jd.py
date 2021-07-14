#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription:

'''
https://search.jd.com/Search?keyword=%E5%B9%B3%E6%9D%BF&wq=%E5%B9%B3%E6%9D%BF&pvid=2e7742653b0541028f4d09ae7616a258&page=3&s=56&click=0
https://search.jd.com/Search?keyword=%E5%B9%B3%E6%9D%BF&wq=%E5%B9%B3%E6%9D%BF&pvid=2e7742653b0541028f4d09ae7616a258&page=5&s=117&click=0
'''


import scrapy
import logging


logger = logging.getLogger(__name__)


class JdSpider(scrapy.Spider):
    name = 'jd'
    # allowed_domains = ['jd.com']
    # start_urls = ['https://dc.3.cn/category/get']
    start_urls = ['https://list.jd.com/list.html?cat=670,671,2694']

    '''
    https://list.jd.com/listNew.php?cat=670%2C671%2C2694&pvid=afb5bca42bd84d58a388493a755f45ca&page=2&s=27&scrolling=y&log_id=1625647589122.5878&tpl=1_M&isList=1&show_items=100017974286,100015470344,100008939415,100009090281,100017974282,100017974302,72493596473,10021713150869,10021720149538,10026614159764,100022491836,100017242702,71810342874,10021713150887,100011203379,100019501386,100011715027,100009075227,10031071600706,100011203375,100009075171,100017242658,100016031040,100022491848,10031989707166,100020961254,10024522592398,10021065426554,100007815187,100017974258
    https://list.jd.com/listNew.php?cat=670%2C671%2C2694&pvid=afb5bca42bd84d58a388493a755f45ca&page=2&s=27&scrolling=y&log_id=1625647589122.5878&tpl=1_M&isList=1&show_items=100017974286
    '''
    def parse(self, response):
        ul = response.xpath('//*[@id="J_goodsList"]/ul/li').extract()
        logger.warning(ul)
        logger.warning(len(ul))
