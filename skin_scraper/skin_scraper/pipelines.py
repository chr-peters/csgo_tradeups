# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sys
sys.path.append("..") # this resolves import issues
from csgo_database.skinsdb import SkinDB
from skin_scraper.items import FloatItem


class SkinScraperPipeline(object):

    def __init__(self):
        self.skindb = SkinDB()

    def process_item(self, item, spider):
        if isinstance(item, FloatItem):
            # insert float item if not in database
            if self.skindb.get_float(weapon=item['weapon'], name=item['name']) is None:
                self.skindb.insert_float(weapon=item['weapon'], name=item['name'], min_float=item['min_float'],
                                         max_float=item['max_float'])
        else:
            # insert skin item if not in database
            if self.skindb.get_skin(weapon=item['weapon'], name=item['name'], quality=item['quality'],
                                    stat_trak=item['stat_trak']) is None:
                self.skindb.insert_skin(weapon=item['weapon'], name=item['name'], rarity=item['rarity'],
                                        collection=item['collection'], quality=item['quality'],
                                        stat_trak=item['stat_trak'], url=item['url'])
        return item
