from scrapy.spiders import CrawlSpider
from price_comparison.items import PriceComparisonItem
from scrapy import Request
from re import search
from urllib.parse import urlencode
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
def get_scrapeops_url(url):
    payload = {'api_key': settings['SCRAPEOPS_API_KEY'], 'url': url,'render_js': True}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url


class AmazonSpider(CrawlSpider):
    name = "amazonscraper"
    queries = ['twice kpop']

    def start_requests(self):
        for query in self.queries:
            url = 'https://www.amazon.com/s?' + urlencode({'k': query})
            yield Request( url=get_scrapeops_url(url), callback=self.parse)

    def parse(self, response):
        products = response.xpath('//*[@data-asin]')

        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f"https://www.amazon.com/dp/{asin}"
            yield Request( url=get_scrapeops_url(product_url), callback=self.parse_item, meta={'url':product_url})

        next_page = response.xpath(
            '//a[@class="s-pagination-item s-pagination-button"][1]/@href').extract_first()
        if next_page:
            url = response.urljoin("https://www.amazon.com", next_page)
            yield Request( url=get_scrapeops_url(url), callback=self.parse)

    def parse_item(self, response):
        if any(x in response.xpath('//*[@id="productTitle"]/text()').extract_first().lower() for x in ["twice", "yes i am", "im nayeon"]):
            product = PriceComparisonItem()
            price = response.xpath('//*[@class="a-price-whole"]/text()').extract_first() + '.' + response.xpath('//*[@class="a-price-fraction"]/text()').extract_first()
            product["image_url"] = search(
                '"large":"(.*?)"', response.text).groups()[0]
            product["title"] = response.xpath(
                '//*[@id="productTitle"]/text()').extract_first().strip()
            product["price"] = price or '0'
            product["url"] = response.meta['url']
            yield product
