import requests
import time
import re
import random
from csgo_database.skinsdb import SkinDB


class ItemNameIdFetcher:
    min_wait = 13
    max_wait = 14
    last_request_time = time.time()

    # these headers are sent with every GET request
    base_headers = {
        'Accept-Language': 'en-US',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
    }

    def get_item_name_id(self, url):
        """Parses the item_name_id from a listing url which is needed to get the buy order and sell order histograms."""

        # make the request to the listing url
        self.__wait()
        res = requests.get(url=url, headers=self.base_headers)
        # res = self.proxy_requests.get(url=url, headers=self.base_headers)

        if not res.ok:
            print('Request not successful! Status code: {}, reason: {}.'.format(res.status_code, res.reason))
            return None

        # the item id is hidden in the javascript, so use a regex
        match = re.search('Market_LoadOrderSpread\\((.*)\\)', res.text)

        try:
            item_id = match.group(1).strip()
            return item_id
        except IndexError:
            return None
        except AttributeError:
            return None

    def __wait(self):
        """Waits before the next request"""
        elapsed_time = time.time() - self.last_request_time
        wait_time = random.uniform(self.min_wait, self.max_wait)
        sleep_time = max(0, wait_time - elapsed_time)
        time.sleep(sleep_time)
        self.last_request_time = time.time()


if __name__ == '__main__':
    fetcher = ItemNameIdFetcher()
    skindb = SkinDB()
    skins_without_id = skindb.get_skins_without_id()
    counter = 1
    for cur_skin in skins_without_id:
        cur_nameid = fetcher.get_item_name_id(cur_skin['url'])
        if cur_nameid is not None:
            skindb.insert_item_nameid(weapon=cur_skin['weapon'], name=cur_skin['name'], quality=cur_skin['quality'],
                                      stat_trak=cur_skin['stat_trak'], nameid=cur_nameid)
            print('{} from {} scanned.'.format(counter, len(skins_without_id)))
        else:
            print('Skin without nameid: {}'.format(cur_skin))
        counter += 1
