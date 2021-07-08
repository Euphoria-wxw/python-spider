#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription:

import scrapy
import copy
import logging
import re
from MyScrapy.items import SNbookItem
from selenium import webdriver
# 实现规避检测
from selenium.webdriver import ChromeOptions
# 无头浏览器设置(无可视化界面)
from selenium.webdriver.chrome.options import Options


logger = logging.getLogger(__name__)


class SnbookSpider(scrapy.Spider):
    name = 'snbook'
    # allowed_domains = ['book.suning.com','list.suning.com']
    start_urls = ['https://book.suning.com/?safp=d488778a.homepagev8.126605238652.1&safpn=10001']
    all_book_href = {}

    def __init__(self):
        # 关闭“chrome正受到自动测试软件的控制”
        option = ChromeOptions()
        option.add_experimental_option('useAutomationExtension', False)
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 无头浏览器设置
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome('/Users/wangxiaowei/Desktop/PythonCode/chromedriver',
                                       chrome_options=chrome_options, options=option)

    def parse(self, response):
        menu_item = response.xpath('/html/body/div[6]/div/div[1]/div[1]/div[1]/div')[:9]
        menu_sub = response.xpath('/html/body/div[6]/div/div[1]/div[1]/div[1]/div')[9:-1]

        for i, mli in enumerate(menu_item):
            item = SNbookItem()
            item['b_cate'] = mli.xpath('./dl/dt/h3/a/text()').extract_first()
            sli = menu_sub[i]
            sub_menu_item = sli.xpath('./div[1]/p')
            book_name_list = sli.xpath('./div[1]/ul')
            if len(sub_menu_item) != 0:
                for j, smi in enumerate(sub_menu_item):
                    item['s_cate'] = smi.xpath('./a/text()').extract_first()
                    bnl = book_name_list[j]
                    book_list = bnl.xpath('./li')
                    for bl in book_list:
                        # 最小标题名
                        item['ms_cate'] = bl.xpath('./a/text()').extract_first()
                        # 最小标题链接
                        item['ms_href'] = bl.xpath('./a/@href').extract_first()

                        self.all_book_href[item['ms_cate']] = item['ms_href']

                        yield scrapy.Request(
                            url=item['ms_href'],
                            callback=self.parse_book_list,
                            dont_filter=True,
                            meta={'item': copy.deepcopy(item)}
                        )
            else:
                book_name_list_li = sli.xpath('./div[1]/ul/li')
                for bl in book_name_list_li:
                    item['s_cate'] = item['b_cate']
                    # 最小标题名
                    item['ms_cate'] = bl.xpath('./a/text()').extract_first()
                    # 最小标题链接
                    item['ms_href'] = bl.xpath('./a/@href').extract_first()

                    self.all_book_href[item['ms_cate']] = item['ms_href']
                    yield scrapy.Request(
                        url=item['ms_href'],
                        dont_filter=True,
                        callback=self.parse_book_list,
                        meta={'item': copy.deepcopy(item)}
                    )

    def parse_book_list(self, response):

        item = response.meta['item']
        book_list_li = response.xpath('//*[@id="filter-results"]/ul/li')
        book_price_list = re.findall('datasku="(.*?)\|\|\|\|\|(.*?)"', response.body.decode())

        for i, li in enumerate(book_list_li):
            item['book_name'] = li.xpath('./div/div/div/div[2]/p[2]/a/text()').extract_first()
            if item['book_name'] is None:
                item['book_name'] = li.xpath('./div/div/div/div[2]/p[3]/a/text()').extract_first()
            # item['book_name'] = item['book_name'].strip('\n')
            # 构造价格获取所需的请求url
            zero = (18 - len(book_price_list[i][0])) * '0'
            book_priId = zero + book_price_list[i][0]
            book_shopid = book_price_list[i][1]
            item['book_price_href'] = 'https://ds.suning.com/ds/generalForTile/{}__2_{}-010-2--1--.jsonp?'.format(
                book_priId, book_shopid)
            item['book_href'] = 'https://' + li.xpath('./div/div/div/div[1]/div/a/@href').extract_first()

            yield scrapy.Request(
                url=item['book_href'],
                callback=self.parse_book_detail,
                dont_filter=True,
                meta={'item': copy.deepcopy(item)}
            )

        # 翻页处理,由于使用了selenium处理response，所以直接获取下一页链接即可
        # 取得下一页链接
        page = response.xpath('//*[@id="nextPage"]/@href').extract_first()

        if page is not None:
            # 以图书列表页域名拼接下一页链接
            page_next = item['ms_href'].split('/')[0] + '//' + item['ms_href'].split('/')[2] + page
            yield scrapy.Request(
                url=page_next,
                callback=self.parse_book_list,
                dont_filter = True,
                meta={'item': copy.deepcopy(item)}
            )


    # 获取详情页信息
    def parse_book_detail(self, response):
        item = response.meta['item']
        # 作者
        item['book_author'] = response.xpath('//*[@id="bookconMain"]/dl/dd/ul/li[1]/span/text()').extract_first()
        # 出版社
        item['book_pb'] = response.xpath('//*[@id="bookconMain"]/dl/dd/ul/li[2]/text()').extract_first()

        yield scrapy.Request(

            url=item['book_price_href'],
            callback=self.parse_book_price,
            dont_filter=True,
            meta={'item': copy.deepcopy(item)}
        )

    # 获取价格
    def parse_book_price(self, response):
        item = response.meta['item']
        # 价格
        item['book_price'] = re.findall('"snPrice":"(.*?)"', response.body.decode())[0]
        if item['book_price'] == '':
            item['book_price'] = 0.0
        else:
            item['book_price'] = float(item['book_price'])

        # logger.warning(item)
        yield item

