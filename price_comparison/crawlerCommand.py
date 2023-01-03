from price_comparison.spiders.Amazon_spider import AmazonSpider
from price_comparison.spiders.Cultura_spider import CulturaSpider
from price_comparison.spiders.Taiyou_spider import TaiyouSpider
from price_comparison.spiders.Musica_spider import MusicaSpider
from scrapy.crawler import CrawlerProcess
import firebase_admin
from firebase_admin import credentials
from scrapy.utils.project import get_project_settings

def main():
    
    settings = get_project_settings()
    FIREBASE_CREDENTIALS= settings['FIREBASE_CREDENTIALS']
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred, {
            'databaseURL': settings['FIREBASE_DATABASE']
	})

    process = CrawlerProcess(settings)
    process.crawl (AmazonSpider) 
    process.crawl (TaiyouSpider) 
    process.crawl (MusicaSpider) 
    process.crawl (CulturaSpider) 
    process.start()
    print ("Crawling Done")

if __name__ == '__main__':
    main()