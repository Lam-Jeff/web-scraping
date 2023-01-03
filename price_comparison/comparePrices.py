import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from scrapy.utils.project import get_project_settings
from firebase_admin import db
from datetime import datetime
import model
import pandas as pd

def findMinPrice():
        load_dotenv()
        # Database Connection

        
        settings = get_project_settings()
        FIREBASE_CREDENTIALS= settings['FIREBASE_CREDENTIALS']
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred, {
                'databaseURL': settings['FIREBASE_DATABASE']
                })

        ref_Cultura = db.reference('/Cultura')
        ref_Musica = db.reference('/Musica')
        ref_Amazon = db.reference('/Amazon')
        ref_Taiyou = db.reference('/Taiyou')
        data_Cultura = ref_Cultura.get()
        data_Musica = ref_Musica.get()
        data_Amazon = ref_Amazon.get()
        data_Taiyou = ref_Taiyou.get()

        results = pd.DataFrame(columns=['shop','external_name', 'internal_name', 'price'])

        df_groundTruth = model.loadData()
        model_trained, df = model.buildModel(df_groundTruth)

        PROJECT_PATH = os.getenv('PROJECT_PATH')
        date=datetime.now()
        date_time_str = date.strftime("%Y-%m-%d")

        for key, value in data_Cultura.items():
                match = model.findMatch (value, df, model_trained)
                row = {'shop': 'Cultura',
                        'external_name': value['title'],
                        'internal_name': match,
                        'price': value['price'],
                        'url': value['url']}
                results = results.append(row, ignore_index=True)
        for key, value in data_Amazon.items():
                match = model.findMatch (value, df, model_trained)
                row = {'shop': 'Amazon',
                        'external_name': value['title'],
                        'internal_name': match,
                        'price': value['price'],
                        'url': value['url']}
                results = results.append(row, ignore_index=True)
        for key, value in data_Musica.items():
                match = model.findMatch (value, df, model_trained)
                row = {'shop': 'Musica',
                        'external_name': value['title'],
                        'internal_name': match,
                        'price': value['price'],
                        'url': value['url']}
                results = results.append(row, ignore_index=True)
        for key, value in data_Taiyou.items():
                match = model.findMatch (value, df, model_trained)
                row = {'shop': 'Taiyou',
                        'external_name': value['title'],
                        'internal_name': match,
                        'price': value['price'],
                        'url': value['url']}
                results = results.append(row, ignore_index=True)
        results = results[results['price'] != '0']
        results['price'] = results['price'].astype (float)
        bestPrices = results[results['price'] == results.groupby('internal_name')['price'].transform(min)].reset_index(drop=True)
        bestPrices.drop(['external_name'], axis=1)
        bestPrices.to_csv(PROJECT_PATH + f'/data/pricecomparison/priceComparisonInfo_{date_time_str}.csv', sep='\t', encoding='utf-8', index=False, header=True)

if __name__ == '__main__':
        findMinPrice()