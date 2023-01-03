from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
BOT_NAME = 'price_comparison'

SPIDER_MODULES = ['price_comparison.spiders']
NEWSPIDER_MODULE = 'price_comparison.spiders'

PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
PLAYWRIGHT_MAX_CONTEXTS = 8

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'price_comparison.middlewares.DomainlimitMiddleware': 543,
    'price_comparison.middlewares.ScrapeOpsFakeBrowserHeadersMiddleware': 400,
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "firefox"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 5
CONCURRENT_REQUESTS = 6
DOWNLOAD_DELAY = 5
MAX_REQUESTS_PER_DOMAIN = 50000
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS = 300
# Retry many times since proxies often fail
RETRY_TIMES = 10
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]


# Scrape Ops
SCRAPEOPS_FAKE_HEADERS_ENABLED= True
SCRAPEOPS_NUM_RESULTS=100
SCRAPEOPS_PROXY_ENABLED= True
SCRAPEOPS_API_KEY= os.getenv ('SCRAPEOPS_KEY')

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    #'price_comparison.middlewares.PriceComparisonSpiderMiddleware': 543,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 543
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'spidermon.contrib.scrapy.pipelines.ItemValidationPipeline': 100,
    'price_comparison.pipelines.CleanStrings': 200,
    'price_comparison.pipelines.InsertValueIntoDatabasePipeline': 400,

}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

FEEDS = {
    'data/%(name)s/%(name)s_%(time)s.csv': {
        'format': 'csv',
        'encoding': 'utf8',
        'store_empty': False,
        'item_classes': "",
        'fields': None,
        'indent': 4,
    }
}

# Replace project-id to yours.
FIREBASE_DATABASE = os.getenv('FIREBASE_URL')
FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS')
# Insert an appropriate value.
FIREBASE_REF = ''
# To compose more robust child paths, you can add a list of properties.
FIREBASE_KEYS = ['uid', 'spider_name']

LOG_LEVEL = 'DEBUG'
#LOG_FILE =
SPIDERMON_ENABLED = True

EXTENSIONS = {
    'spidermon.contrib.scrapy.extensions.Spidermon': 500,
}
SPIDERMON_SPIDER_CLOSE_MONITORS = (
    'price_comparison.monitors.SpiderCloseMonitorSuite',
)
SPIDERMON_VALIDATION_MODELS = (
    'price_comparison.validators.ProductItem',
)

SPIDERMON_REPORT_CONTEXT = {
    'report_title': 'Spidermon File Report'
}
date = datetime.now()
date_time_str = date.strftime("%Y-%m-%d")
SPIDERMON_REPORT_FILENAME = os.getenv(
    'PROJECT_PATH') + f'/logs/log_{date_time_str}.html'
SPIDERMON_REPORT_TEMPLATE = 'reports/email/monitors/result.jinja'

STATS_CLASS = (
    "spidermon.contrib.stats.statscollectors.local_storage.LocalStorageStatsHistoryCollector"
)

# Stores the stats of the last 10 spider execution (default=100)
SPIDERMON_MAX_STORED_STATS = 10
