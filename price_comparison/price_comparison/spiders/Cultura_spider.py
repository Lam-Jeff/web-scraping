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

class CulturaSpider(CrawlSpider):
    name = "culturascraper"
    base_link = 'https://www.cultura.com'


    def start_requests(self):
        yield Request(
            url=get_scrapeops_url("https://www.cultura.com/musique/genres-musicaux/kpop.html?artiste_principal=Twice"),
            callback=self.parse
        )

    def parse(self, response):
        products_selector = response.xpath('//a[@class="one-product one-product--plp"]')
        for product in products_selector:
            url = self.base_link + product.xpath('.//@href').extract_first()
            link = response.urljoin(url)
            yield Request( url=get_scrapeops_url(link), callback=self.parse_product, meta ={'url': url})

    def parse_product(self, response):
        product = PriceComparisonItem()
        product["image_url"] = response.xpath(
            '//div[@id="swiper-pdp-pictures"]/div/div/div/div/picture/source[1]/@srcset').extract_first()
        product["title"] = response.css(
            "div.aem-GridColumn.aem-GridColumn--default--12.aem-GridColumn--desktop--without500 > div > div > h1::text").extract_first()
        product["price"] = response.css(
            "div.text-right > div::attr(content)").extract_first() or '0'
        product["url"] = response.meta['url']
        yield product
