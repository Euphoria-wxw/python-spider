#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription:


import scrapy
from MyScrapy.items import Tupian4KItem
import logging
import copy

logger = logging.getLogger(__name__)

class Tupian4kSpider(scrapy.Spider):
    name = 'tupian4K'
    # allowed_domains = ['pic.netbian.com']
    start_urls = ['https://pic.netbian.com/new/']

    def parse(self, response):
        classify_list = response.xpath('//*[@id="main"]/div[2]/a')
        for li in classify_list:
            classify_url = 'https://pic.netbian.com' + li.xpath('./@href').extract_first()
            # logger.warning(classify_url)
            item = Tupian4KItem()
            item['path'] = li.xpath('./text()').extract_first()
            # 用以区分第几页数据
            page_num = 1
            yield scrapy.Request(
                url=classify_url,
                callback=self.parse_index,
                meta={'item': item,
                      'pageNum': page_num}
            )

    def parse_index(self, response):
        img_li = response.xpath('//div[@class="slist"]/ul/li')
        item = response.meta['item']
        page_num = response.meta['pageNum']
        item['pageNum'] = page_num

        for li in img_li:
            # 图片名称
            img_name = li.xpath('./a/b/text()').extract_first()

            # 图片详情链接
            img_url_detail = 'https://pic.netbian.com' + li.xpath('./a/@href').extract_first()
            # 图片名获取失败输出日志
            if img_name is None:
                img_name = li.xpath('./a/@alt').extract_first()
                logger.warning('图片名称未获取，板块为：{};页数为：{};链接为：{}'
                               .format(item['path'],page_num, img_url_detail))

            item = response.meta['item']
            item['name'] = img_name + '.jpg'
            item['url_detail'] = img_url_detail
            # logger.warning(item)
            yield scrapy.Request(
                url=img_url_detail,
                callback=self.parse_imgUrl,
                meta={
                    'item': copy.deepcopy(item)
                }
            )

        page = response.xpath('//*[@id="main"]/div[4]/a')[-1].xpath('./@href').extract_first()
        page_next = 'https://pic.netbian.com' + page

        if page_next is not None:
            print('pageNow = ', page_num)
            page_num += 1
            yield scrapy.Request(
                url=page_next,
                callback=self.parse_index,
                meta={'item': item,
                      'pageNum': page_num
                      }
            )

    # 深层解析获取高清图片src
    def parse_imgUrl(self, response):
        img_url = response.xpath('//div[@class="photo-pic"]/a/img/@src').extract_first()
        # 接收item
        item = response.meta['item']
        item['url'] = 'https://pic.netbian.com' + img_url
        yield item
