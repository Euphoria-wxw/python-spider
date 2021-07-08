# Scrapy settings for MyScrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html


BOT_NAME = 'MyScrapy'

SPIDER_MODULES = ['MyScrapy.spiders']
NEWSPIDER_MODULE = 'MyScrapy.spiders'


# 输出日志等级
LOG_LEVEL = 'WARNING'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/89.0.4389.114 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
import datetime
Today=datetime.datetime.now()#取得现在的时间
Log_file_path='scrapy_{}_{}_{}.log'.format(Today.year,Today.month,Today.day)#以时间为文件名
LOG_FILE = Log_file_path
IMAGES_STORE = '/tupian4K'

# redis 设置
# SCHEDULER = "scrapy_redis.scheduler.Scheduler" # 使用scrapy-redis组件自己的调度器
# DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'  # 去重规则对应处理的类
# SCHEDULER_PERSIST = True # 是否在关闭时候保留，调度器和去重记录
# REDIS_HOST = 'localhost'  # 远程服务器地址/主机名
# REDIS_PORT = 6379  # 端口


# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# RANDOMIZE_DOWNLOAD_DELAY=True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False
# COOKIES_DEBUG = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     # 'Accept-Language': 'en',
#     'referer': "https://m.jd.com/"
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'MyScrapy.middlewares.MyscrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'MyScrapy.middlewares.MyscrapyDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'MyScrapy.pipelines.Tupian4KPipeLine': 300,
    'MyScrapy.pipelines.SNbookPipeline': 300,
    # 'scrapy_redis.pipelines.RedisPipeline': 400
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
