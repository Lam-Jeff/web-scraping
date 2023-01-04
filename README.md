### Objectives 
- Learn to use Scrapy framework
- Short introduction on how to send messages to the discord software. 
- personal app

### What does my app do
- The purpose of the project is to scrap several websites in order to compare the price of products and return the best price for a given product.
- First, several spiders are going to crawl different websites (four in total) and store the results in a Firebase database.
- Next, we need to compare the prices.In order to do that, the project has a product matching model. A machine learning model will match the products by their titles. It then return the best prices between them. The results are sent to a private discord.
- All the results produced by the project are saved as csv files. There is a script to clean these files.
- To schedule the scrapings, the project has a Cronjob which allows to schedule tasks locally.

### Techs, softwares, librairies…
- Firefox
- Vscode 
- Github Desktop
- Crontab
- Scrapy playwright / Scrapy
- Discord
- Firebase
- sklearn

### Limits
The project is limited by ScrapeOps service. We have a limit of 1000 requests  per month with proxies.

### Credits
- how to schedule tasks locally :
https://m-t-a.medium.com/running-scrapy-spiders-locally-in-a-cron-job-4ce49f42678b
- how to send messages to your discord :
 https://www.youtube.com/watch?v=klLeRzUg6HA
 - build a product matching model : 
 https://practicaldatascience.co.uk/machine-learning/how-to-create-a-product-matching-model-using-xgboost
 - fake headers and proxies : 
 https://scrapeops.io/docs/intro/
