#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : wang
# @Software: PyCharm
# @FileName:
# @FileDescription: 京东登录cookies只能用chrome中手机模式获取的的


import scrapy
import json
import copy


class JingdongSpider(scrapy.Spider):
    """
    爬取京东商品评论
    """
    name = 'jingdong'
    allowed_domains = ['club.jd.com']
    # 京东评论链接 maxpage-最大页数 100021399616-商品ID
    start_urls = ['https://club.jd.com/comment/productPageComments.action?productId=100021399616&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0']
    # start_urls = ['https://p.m.jd.com/cart/cart.action?fromnav=1']  # 京东cookies
    pageNext_url = 'https://club.jd.com/comment/productPageComments.action?productId=100021399616&score=0&sortType=0&page={}&pageSize=10&isShadowSku=0'

    def make_requests_from_url(self, url):
        """ This method is deprecated. """
        return scrapy.Request(url, dont_filter=False)

    def parse(self, response):
        item = {}
        comments = response.body.decode('gbk')
        comments = json.loads(comments)
        maxPage = comments['maxPage']
        for comment in comments['comments']:
            item['id'] = comment['id']
            item['comtent'] = comment['content']
            print(item)
            yield item


        for i in range(1,maxPage-1):
            yield scrapy.Request(
                url=self.pageNext_url.format(i),
                callback=self.parse,
                # meta={'item': copy.deepcopy(item)}
            )

