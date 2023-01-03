from scrapy.spiders import CrawlSpider
from price_comparison.items import PriceComparisonItem
from scrapy import Request
from urllib.parse import urlencode
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

def get_scrapeops_url(url):
    payload = {'api_key': settings['SCRAPEOPS_API_KEY'], 'url': url,'render_js': True}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

class TaiyouSpider(CrawlSpider):
    name = "taiyouscraper"
    base_link = "https://www.taiyou.fr"
        

    def start_requests(self):
        yield Request(
            url=get_scrapeops_url(
                "https://www.taiyou.fr/ps3/kpop/girlsband/twice/1829,1,2/1.html"),
            callback=self.parse
        )

    def parse(self, response):
        products_selector = response.xpath('//div[@class="article_0"]')
        for product in products_selector:
            url = self.base_link + product.xpath('.//h2[@class="title"]//a[text()]/@href').extract_first()
            link = response.urljoin(url)
            yield Request(url=link, callback=self.parse_product, meta={'url': url})

    def parse_product(self, response):
        product = PriceComparisonItem()
        product["image_url"] = response.urljoin(response.css(
            "div.item > a > img.img-responsive::attr(src)").extract_first())
        product["title"] = response.css(
            "div.entry-header.product_pad > header > h1::text").extract_first()
        product["price"] = response.css(
            "#center_column > article > div.container.bg.pabs > div.row > div.col-xs-12.col-sm-8 > form > div.info_product > div > div:nth-child(2) > div > span > span.dyn_devise_price::text").extract_first() or '0'
        product["url"] = response.meta['url']
        yield product
