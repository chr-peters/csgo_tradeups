# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sys
sys.path.append("..") # this resolves import issues
from csgo_database.skinsdb import SkinDB


class SkinScraperPipeline(object):

    def __init__(self):
        self.skindb = SkinDB()

    def process_item(self, item, spider):
        # select skin if not already in database
        if self.skindb.get_skin(item['weapon'], item['name']) is None:
            self.skindb.insert_skin(item['weapon'], item['name'], item['rarity'], item['collection'])
        return item
