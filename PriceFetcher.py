import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json


class PriceFetcher:

    min_wait = 1
    max_wait = 3
    last_request_time = time.time()

    # these headers are send with every GET request
    base_headers = {
        'Accept-Language': 'en-US',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
    }

    def fetch_prices(self, weapon, name, quality, stat_track):
        # get the url of the listing
        listing_url = self.__get_skin_listing_url(weapon, name, quality, stat_track)
        if listing_url is None:
            return None

        # now get the id of the item which is needed to get the buy and sell order histograms
        item_name_id = self.__get_item_name_id(listing_url)
        if item_name_id is None:
            return None

        # make the request to the histogram api
        url = 'https://steamcommunity.com/market/itemordershistogram'
        params = {
            'country': 'DE',
            'language': 'english',
            'currency': 3,  # 1: dollar, 2: pound, 3: euro
            'item_nameid': item_name_id,
            'two_factor': 0
        }
        self.__wait()
        res = requests.get(url=url, params=params, headers=self.base_headers)
        try:
            res_json = json.loads(res.text)
        except json.decoder.JSONDecodeError:
            return None

        # get the max. 10 lowest sell prices
        sell_prices = []
        try:
            for cur_price_level in res_json['sell_order_graph']:
                if len(sell_prices) >= 10:
                    break
                for i in range(cur_price_level[1] - len(sell_prices)):
                    sell_prices.append(cur_price_level[0])
                    if len(sell_prices) > 10:
                        break

            # build the result
            result = {
                'highest_buy_order': res_json['buy_order_graph'][0][0],
                'lowest_sell_orders': sell_prices
            }

            return result
        except KeyError:
            return None

    def __get_skin_listing_url(self, weapon, name, quality, stat_track):
        """Returns the url of a skin listing."""

        # build the search query
        query = ''
        if stat_track:
            query = query + 'StatTrak™ '
        query = query + weapon + ' | ' + name + ' (' + quality + ')'

        # make the GET-Request
        url = 'https://steamcommunity.com/market/search'
        params = {
            'appid': 730,
            'q': '"' + query + '"'
        }
        self.__wait()
        res = requests.get(url, params=params, headers=self.base_headers)

        # extract the resulting url
        bs = BeautifulSoup(res.text, features='lxml')
        result_rows = bs.select('a.market_listing_row_link')
        # filter through the rows to find the right skin
        for cur_row in result_rows:
            cur_title = cur_row.select('span.market_listing_item_name')[0].string
            if cur_title == query:
                return cur_row['href']

        return None

    def __wait(self):
        """Waits before the next request"""
        elapsed_time = time.time() - self.last_request_time
        wait_time = random.uniform(self.min_wait, self.max_wait)
        sleep_time = max(0, wait_time - elapsed_time)
        time.sleep(sleep_time)
        self.last_request_time = time.time()

    def __get_item_name_id(self, url):
        """Parses the item_name_id from a listing url which is needed to get the buy order and sell order histograms."""

        # make the request to the listing url
        self.__wait()
        res = requests.get(url=url, headers=self.base_headers)

        # the item id is hidden in the javascript, so use a regex
        match = re.search('Market_LoadOrderSpread\\((.*)\\)', res.text)

        try:
            item_id = match.group(1).strip()
            return item_id
        except IndexError:
            return None


if __name__ == '__main__':
    priceFetcher = PriceFetcher()
    print(priceFetcher.fetch_prices(weapon='MAG-7', name='Justice', quality='Factory New', stat_track=False))
    #print(priceFetcher.fetch_prices(weapon='AWP', name='Dragon Lore', quality='Factory New', stat_track=False))
    #print(priceFetcher.fetch_prices(weapon='AWP', name='Dragon Lore', quality='Battle-Scarred', stat_track=False))
    #print(priceFetcher.fetch_prices(weapon='asdf', name='asdf', quality='asdf', stat_track=False))
