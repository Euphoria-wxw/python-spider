# -*- coding: utf-8 -*-
import scrapy, copy, re, json
from scrapy_redis.spiders import RedisSpider

class DangdangSpider(RedisSpider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com','e.dangdang.com']
    # start_urls = ['http://book.dangdang.com/']
    redis_key = 'dangdang'

    data = {
        'action': 'mediaCategoryLeaf',
        'promotionType': '1',
        'deviceSerialNo': 'html5',
        'macAddr': 'html5',
        'channelType': 'html5',
        'permanentId': '20210107102231342412365874956951972',
        'returnType': 'json',
        'channelId': '70000',
        'clientVersionNo': '5.8.4',
        'platformSource': 'DDDS-P',
        'fromPlatform': '106',
        'deviceType': 'pconline',
        'token': '',
        'start': '0',
        'end': '0',
        'category': '',
        'dimension': 'dd_sale'
    }
    def parse(self, response):
        """
        图书分类页
        :param response:
        """
        div_list = response.xpath('//div[@class="con flq_body"]/div')
        for div in div_list:
            item = {}
            # 大分类
            item['b_cate'] = div.xpath('./dl/dt//text()').extract()
            # 去空格和换行符
            item['b_cate'] = [i.strip() for i in item['b_cate'] if len(i.strip())>0]
            if len(item['b_cate']) > 0:
                item['b_cate'] = ''.join(item['b_cate'] )
            dl_list = div.xpath('./div//dl[@class="inner_dl"]')
            for dl in dl_list:
                # 中分类
                item['s_cate'] = dl.xpath('./dt//text()').extract()
                item['s_cate'] = [i.strip() for i in item['s_cate'] if len(i.strip())>0][0]
                dd_list = dl.xpath('./dd/a')
                # print(item)
                for dd in dd_list:
                    # 最小分类
                    item['ss_cate'] = dd.xpath('./@title').extract_first()
                    item['ss_href'] = dd.xpath('./@href').extract_first()

                    if item['ss_href'] is not None:
                        yield scrapy.Request(
                            url=item['ss_href'],
                            callback=self.parse_book_list,
                            meta={'item':copy.deepcopy(item)}
                        )

        # 翻页
        page = response.xpath('//div[@class="paging"]//li[@class="next"]/a/@href').extract_first()
        if page is not None:
            page_next = item['ss_href'].split('/')[0] + '//' + item['ss_href'].split('/')[2] + page
            yield scrapy.Request(
                url=page_next,
                callback=self.parse,
                meta={'item': copy.deepcopy(item)}
            )

    def parse_book_list(self, response):
        """
        图书列表页
        :param response:
        """
        item = response.meta['item']
        # print(item['ss_href'])
        if 'category' in item['ss_href'] or 'search' in item['ss_href']:
            li_list = response.xpath('//ul[@class="bigimg"]/li')
            for li in li_list:
                item['book_price_n'] = li.xpath('.//span[@class="search_now_price"]/text()').extract_first()
                item['book_price_n'] = float(item['book_price_n'].split('¥')[1])

                item['book_title'] = li.xpath('./a/@title').extract_first()
                item['book_word'] = li.xpath('./p[@class="detail"]/text()').extract_first()
                if item['book_word'] is None:
                    item['book_word'] = '无'
                item['book_comments_href'] = 'http:' + li.xpath('./p[@class="search_star_line"]/a/@href').extract_first()
                item['book_comments_num'] = li.xpath('./p[@class="search_star_line"]/a/text()').extract_first().strip('条评论')
                item['book_comments_num'] = int(item['book_comments_num'])
                item['book_detail_href'] = 'http:' + li.xpath('./a/@href').extract_first()

                item['book_author'] = li.xpath('./p[@class="search_book_author"]/span[1]/a[1]/text()').extract_first()
                item['book_pd'] = li.xpath('./p[@class="search_book_author"]/span[3]/a/text()').extract_first()
                # print(item)
                yield item

        elif 'e.dangdang' in item['ss_href']:
            if 'classification_list' in item['ss_href']:
                # self.data['start'] = '0'
                # self.data['end'] = '0'
                self.data['category'] = re.findall('category=(.*?)&',item['ss_href'])[0]
                print('classification: ' + item['ss_href'])

                yield scrapy.FormRequest(
                    url='http://e.dangdang.com/media/api.go',
                    method='GET',
                    formdata= self.data,
                    callback= self.parse_e_dangdang_com,
                    meta={'item':copy.deepcopy(item), 'start':1, 'end':0}
                )
            else:
                print(item['ss_href'])

    def parse_e_dangdang_com(self, response):
        """
        先请求一次获取总条数total，然后按每页80条获取数据
        :param response:
        """
        item = response.meta['item']
        start = response.meta['start']
        end = response.meta['end']
        data = response.body.decode()
        data = json.loads(data)
        saleList = data['data']['saleList']
        total = int(data['data']['total'])
        code = data['data']['code']
        print('total=',total)
        print('code=',code)
        print('start=',start,'end=',end)
        print(len(saleList))

        if len(saleList) == 0:
            print(response.status)
            print(response.url)
        elif len(saleList) == 1:
            try:
                item['book_title'] = saleList[0]['mediaList'][0]['title']
                item['book_word'] = saleList[0]['mediaList'][0]['descs'].strip()
                item['book_price_n'] = saleList[0]['mediaList'][0]['salePrice']
                item['book_author'] = saleList[0]['mediaList'][0]['authorPenname']
            except KeyError as e:
                item['book_price_n'] = saleList[0]['mediaList'][0]['price']
                print('错误位置：', item['book_title'], '错误原因：', e)
            print(item)
            yield item
        else:
            for li in saleList:
                try:
                    item['book_title'] = li['mediaList'][0]['title']
                    item['book_word'] = li['mediaList'][0]['descs'].strip()
                    item['book_price_n'] = li['mediaList'][0]['salePrice']
                    item['book_author'] = li['mediaList'][0]['authorPenname']
                    print(item)
                    yield item
                except KeyError as e:
                    item['book_price_n'] = li['mediaList'][0]['price']
                    print('错误位置：', item['book_title'], '错误原因：', e)
        # 换页
        if end < total:
            self.data['start'] = str(start)
            end += 80 if (total - end) // 80 > 0 else total % 80
            self.data['end'] = str(end)
            start = end + 1
            self.data['category'] = code

            yield scrapy.FormRequest(
                url='http://e.dangdang.com/media/api.go',
                method='GET',
                formdata=self.data,
                callback=self.parse_e_dangdang_com,
                meta={'item': copy.deepcopy(item),'start':start, 'end':end}
            )
