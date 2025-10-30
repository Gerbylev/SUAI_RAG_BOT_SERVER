# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OutSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ContentItem(scrapy.Item):
    url = scrapy.Field()
    content_type = scrapy.Field()
    filename = scrapy.Field()
    raw_content = scrapy.Field()
    cleaned_content = scrapy.Field()
    text_content = scrapy.Field()