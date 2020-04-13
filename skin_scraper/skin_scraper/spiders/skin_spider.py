import scrapy
from ..items import SkinItem

class SkinSpider(scrapy.Spider):

    name = "skin_spider"

    start_urls = ["https://www.csgodatabase.com/weapons/"]

    knife_urls = ['/weapons/bayonet/', '/weapons/bowie-knife/']

    def parse(self, response):
        """Parses the weapon page of the csgo database by extracting and following the links to all weapons."""
        linklist = response.css('div.weaponBox a')
        for link in linklist:
            # skip the knifes
            if link.attrib['href'] not in self.knife_urls:
                yield response.follow(link, callback=self.parse_skins)

    def parse_skins(self, response):
        """Parses all skins for a weapon."""
        skinboxes = response.css('div.skin-box')
        for cur_skinbox in skinboxes:
            cur_item = SkinItem()

            # parse title to get weapon and name
            titlestring = cur_skinbox.css('div.skin-box-header a::text').get()
            titleparts = titlestring.split('|')
            cur_item['weapon'] = titleparts[0].strip()
            cur_item['name'] = titleparts[1].strip()

            # parse rarity
            headerparts = cur_skinbox.css('div.skin-box-header').attrib['class'].split()
            if 'CovertSkinBox' in headerparts:
                cur_item['rarity'] = 'Covert'
            if 'ClassifiedSkinBox' in headerparts:
                cur_item['rarity'] = 'Classified'
            if 'RestrictedSkinBox' in headerparts:
                cur_item['rarity'] = 'Restricted'
            if 'Mil-specSkinBox' in headerparts:
                cur_item['rarity'] = 'Mil-spec'
            if 'IndustrialSkinBox' in headerparts:
                cur_item['rarity'] = 'Industrial'
            if 'ConsumerSkinBox' in headerparts:
                cur_item['rarity'] = 'Consumer'

            # parse collection
            collectiontext = cur_skinbox.css('div.collection-skinbox::text').get().strip()
            cur_item['collection'] = collectiontext

            yield cur_item
