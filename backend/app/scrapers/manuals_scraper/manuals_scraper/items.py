# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ManualItem(scrapy.Item):
    url = scrapy.Field()
    model = scrapy.Field()
    language = scrapy.Field()
    title = scrapy.Field()
    file_urls = scrapy.Field()  # REQUIRED by FilesPipeline
    files = scrapy.Field()       # REQUIRED by FilesPipeline