# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonTestItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    good_name = scrapy.Field()
    good_url = scrapy.Field()
    price = scrapy.Field()
    star_level = scrapy.Field()
    answers = scrapy.Field()