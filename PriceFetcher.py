import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json
from proxy_requests import ProxyRequests


class PriceFetcher:

    min_wait = 1
    max_wait = 2
    last_request_time = time.time()

    # these headers are sent with every GET request
    base_headers = {
        'Accept-Language': 'en-US',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
    }

    def __init__(self):
        self.proxy_requests = ProxyRequests()

    def fetch_prices(self, item_name_id):

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
        # res = self.proxy_requests.get(url=url, params=params, headers=self.base_headers)

        if not res.ok:
            print('Could not fetch price. Status code: {}, reason: {}'.format(res.status_code, res.reason))
            return None

        try:
            res_json = json.loads(res.text)
        except json.decoder.JSONDecodeError:
            print('Could not decode json.')
            return None

        # get the max. 10 lowest sell prices
        sell_prices = []
        try:
            for cur_price_level in res_json['sell_order_graph']:
                if len(sell_prices) >= 10:
                    break
                for i in range(cur_price_level[1] - len(sell_prices)):
                    sell_prices.append(cur_price_level[0])
                    if len(sell_prices) >= 10:
                        break

            # build the result
            result = {
                'highest_buy_order': round(float(res_json['highest_buy_order'])/100, 2),
                'lowest_sell_orders': sell_prices
            }

            return result
        except KeyError:
            print('Key Error.')
            return None

    def __wait(self):
        """Waits before the next request"""
        elapsed_time = time.time() - self.last_request_time
        wait_time = random.uniform(self.min_wait, self.max_wait)
        sleep_time = max(0, wait_time - elapsed_time)
        time.sleep(sleep_time)
        self.last_request_time = time.time()


if __name__ == '__main__':
    priceFetcher = PriceFetcher()
    print(priceFetcher.fetch_prices('176012395'))
