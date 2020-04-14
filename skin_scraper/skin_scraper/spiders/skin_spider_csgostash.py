import scrapy
from ..items import SkinItem, FloatItem

class SkinSpider(scrapy.Spider):

    name = 'skin_spider_csgostash'

    start_urls = ['https://csgostash.com/']

    def parse(self, response):
        """Parses the home page of csgo stash for the weapon links."""
        dropdown_items = response.css('li.dropdown')
        for cur_dropdown_item in dropdown_items:
            cur_category = cur_dropdown_item.css('a.dropdown-toggle::text').get()
            if cur_category is None:
                continue
            cur_category = cur_category.strip()
            if cur_category not in ['Pistols', 'Rifles', 'SMGs', 'Heavy']:
                continue
            # extract weapon links
            weapon_links = cur_dropdown_item.css('ul li a')
            for cur_weapon_link in weapon_links:
                yield response.follow(cur_weapon_link, callback=self.parse_weapon)

    def parse_weapon(self, response):
        """Parses a weapon page to extract all skin links"""
        skin_links = response.css('div.result-box > a:nth-child(4)')
        for cur_skin_link in skin_links:
            yield response.follow(cur_skin_link, callback=self.parse_skin)

    def parse_skin(self, response):
        # get weapon and skin name
        title_elements = response.css('div.result-box > h2 > a')
        weapon_name = title_elements[0].css('::text').get().strip()
        skin_name = title_elements[1].css('::text').get().strip()

        # get min_float and max_float
        min_float = float(response.css('div.wear-min-value').attrib['data-wearmin'])
        max_float = float(response.css('div.wear-max-value').attrib['data-wearmax'])

        float_item = FloatItem()
        float_item['weapon'] = weapon_name
        float_item['name'] = skin_name
        float_item['min_float'] = min_float
        float_item['max_float'] = max_float

        yield float_item

        # get rarity and collection
        rarity = response.css('div.quality > p::text').get().strip().split()[0]
        collection_containers = response.css('p.collection-text-label')
        if len(collection_containers) == 1:
            collection = collection_containers[0].css('::text').get().strip()
        else:
            collection = collection_containers[1].css('::text').get().strip()

        # get the listing urls
        market_links = response.css('div#prices a')
        for cur_link in market_links:
            if 'href' not in cur_link.attrib.keys() or '/listings/' not in cur_link.attrib['href']:
                continue
            url = cur_link.attrib['href']

            # determine stat_trak and quality
            spans = cur_link.css('span')
            stat_trak = False
            if len(spans) == 3:
                # stat_trak or souvenir
                if spans[0].css('::text').get().strip() == 'StatTrak':
                    stat_trak = True
                else:
                    # ignore souvenir skins because they can't be used in trade-ups
                    continue

                # get quality of stat_trak skin
                quality = spans[1].css('::text').get().strip()
            else:
                quality = spans[0].css('::text').get().strip()

            skin_item = SkinItem()
            skin_item['weapon'] = weapon_name
            skin_item['name'] = skin_name
            skin_item['rarity'] = rarity
            skin_item['collection'] = collection
            skin_item['quality'] = quality
            skin_item['stat_trak'] = stat_trak
            skin_item['url'] = url

            yield skin_item
