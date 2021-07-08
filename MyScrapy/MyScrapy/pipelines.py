# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from MyScrapy.spiders.snbook import logger
from pymongo import MongoClient

client = MongoClient()
collection = client['mongo']['snbook']


class Tupian4KPipeLine(ImagesPipeline):
    # 对item中的图片进行请求操作
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['url'], meta={'item': item})

    # 定制图片的名称
    def file_path(self, request, response=None, info=None, *, item=None):
        # url = request.url
        item = request.meta['item']
        file_name = item['path'] + '/' + '第{}页'.format(item['pageNum']) +'/' + item['name']
        # print(item)
        return file_name

    def item_completed(self, results, item, info):
        return item  # 该返回值会传递给下一个即将被执行的管道类


class SNbookPipeline:
    def process_item(self, item, spider):
        if spider.name == 'snbook':
            item['book_name'].strip('\n')
            logger.warning(item)
            collection.insert(dict(item))
        return item