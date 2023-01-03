# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from firebase_admin import db


class InsertValueIntoDatabasePipeline:

    def process_item(self, item, spider):
        reference =''
        if spider.name in ['taiyouscraper']:
            reference += '/Taiyou'
        elif spider.name in ['musicascraper']:
            reference += '/Musica'
        elif spider.name in ['culturascraper']:
            reference += '/Cultura'
        elif spider.name in ['amazonscraper']:
            reference += '/Amazon'

        ref = db.reference(reference)
        data = ref.get()
        check_exist = False
        if data is not None:
            for key, value in data.items():
                if value['title'] == item['title'] and value['price'] != item['price']:
                    ref.child(key).update({
                        "price": item["price"],
        })
                    check_exist = True

        if not check_exist:
            ref.push().set({
                "title": item['title'],
                "image_url": item["image_url"],
                "price": item["price"],
                "url": item["url"],
            })
        return item

class CleanStrings:
    toReplace =  [('ltd', 'limited'), 
                ('vers', ''),
                ('ver', ''),
                ('vol', ''),
                ('.', ''), 
                ('-', ''),
                ('limitée', 'limited'),
                ('limité', 'limited'),
                ('limitee', 'limited'),
                ('/', ''),
                ('cd', ''),
                ('(', ''),
                (')', ''),
                ('[', ''),
                (']', ''),
                (':', ''),
                ("'", '')
                ]
    def process_item(self, item, spider):
        item['title'] = item['title'].lower()
        item['price'] = item['price'].replace (',', '.') # Musica uses ',' for the decimal
        for k, value in self.toReplace:
            item['title'] = item['title'].replace (k, value)
        return item
