from discord import SyncWebhook, File
import os
import glob
from dotenv import load_dotenv

def sendRequestToDiscord():
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_URL_CODE = os.getenv('DISCORD_URL_CODE')
    PATH_DATA =  os.getenv ('PROJECT_PATH') + '/data'
    webhook = SyncWebhook.partial(DISCORD_URL_CODE, DISCORD_TOKEN)
    files_to_send = []

    # results showing the scraping
    for root, dirs, files in os.walk(PATH_DATA):
            csv_files = glob.glob (root + '/*.csv')
            if csv_files:
                    files_to_send.append(File(max(csv_files, key=os.path.getctime)))

    webhook.send('RECAP OF WEB SCRAPPING: ', 
                username='Captain Scraper',
                files=files_to_send)

if __name__ == '__main__':
    sendRequestToDiscord()