# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SkinItem(scrapy.Item):
    # define the fields for your item here like:
    weapon = scrapy.Field()
    name = scrapy.Field()
    rarity = scrapy.Field()
    collection = scrapy.Field()
    quality = scrapy.Field()
    stat_trak = scrapy.Field()
    url = scrapy.Field()


class FloatItem(scrapy.Item):
    weapon = scrapy.Field()
    name = scrapy.Field()
    min_float = scrapy.Field()
    max_float = scrapy.Field()
