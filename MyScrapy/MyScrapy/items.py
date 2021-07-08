# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SNbookItem(scrapy.Item):
    # define the fields for your item here like:
    # 书名，作者，出版社，价格，详情链接
    # 大分类
    b_cate = scrapy.Field()
    s_cate = scrapy.Field()             # 小分类
    ms_cate = scrapy.Field()            # 最小分类
    ms_href = scrapy.Field()            # 最小分类链接
    book_name = scrapy.Field()          # 书名
    book_price_href = scrapy.Field()    # 价格获取链接
    book_href = scrapy.Field()          # 图书详情页链接
    book_author = scrapy.Field()        # 作者
    book_pb = scrapy.Field()            # 出版社
    book_price = scrapy.Field()         # 图书价格


class Tupian4KItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    path = scrapy.Field()
    url_detail = scrapy.Field()
    pageNum = scrapy.Field()