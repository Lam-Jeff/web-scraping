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

class MusicaSpider(CrawlSpider):
    name = "musicascraper"
    base_link = 'https://www.asiaworldmusic.fr'
    
    start_urls = ["https://www.asiaworldmusic.fr/135-presse-photobook",
                  "https://www.asiaworldmusic.fr/20-groupes-kr",
                  "https://www.asiaworldmusic.fr/328-season-s-greetings-2023",
                  "https://www.asiaworldmusic.fr/220-season-s-greetings-welcome-package",
                  "https://www.asiaworldmusic.fr/52-groupes-jp",
                  "https://www.asiaworldmusic.fr/315-espace-dicon",
                  "https://www.asiaworldmusic.fr/306-espace-jyp"]

    def start_requests(self):

        for url in self.start_urls:
            yield Request(
                url=get_scrapeops_url(url),
                callback=self.parse
            )

    def parse(self, response):
        products_selector = response.xpath('//div[@class="left-block"]')
        for product in products_selector:
            url = product.xpath('.//a[@class="product_img_link"]/@href').extract_first()
            if any(x in url.lower() for x in ["twice", "yes-i-am", "im-nayeon"]):
                yield Request(url=get_scrapeops_url(url), callback=self.parse_product,meta= {'url': url})

        next_page = response.xpath(
            '//li[@class="pagination_next"]/a/@href').extract_first()
        if next_page:
            url = self.base_link + next_page
            yield Request(url=get_scrapeops_url(url), callback=self.parse)

    def parse_product(self, response):
        product = PriceComparisonItem()
        product["image_url"] = response.css("#bigpic::attr(src)").extract_first()
        product["title"] = response.css(
            "div.pb-center-column.col-xs-12.col-sm-12.col-md-6.col-lg-6 > h1::text").extract_first()
        product["price"] = response.css(
            "#our_price_display::text").extract_first().split(' ')[0] or '0'
        product["url"] = response.meta['url']
        yield product
