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
