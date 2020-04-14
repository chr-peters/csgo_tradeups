import requests
import random


class ProxyRequests:

    def __init__(self):
        # get the proxy lists from github
        res = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt')
        self.proxies = res.text.split()
        res = requests.get('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt')
        self.proxies.extend(res.text.split('\n')[2:])
        res = requests.get('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt')
        self.proxies.extend(res.text.split('\n')[2:])
        res = requests.get('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt')
        self.proxies.extend(res.text.split('\n')[2:])

        # remove duplicates
        self.proxies = list(set(self.proxies))

    def get_random_proxy(self):
        try:
            return random.choice(self.proxies)
        except IndexError:
            return None

    def remove_proxy(self, proxy):
        try:
            self.proxies.remove(proxy)
        except ValueError:
            pass

    def get(self, url, timeout=3, **kwargs):
        """Calls requests.get using a proxy from the list"""
        while len(self.proxies) > 0:
            cur_proxy = self.get_random_proxy()
            print('Trying proxy {}, {} proxies left.'.format(cur_proxy, len(self.proxies)))
            proxies = {
                'http': cur_proxy,
                'https': cur_proxy
            }
            try:
                res = requests.get(url, proxies=proxies, timeout=timeout, **kwargs)
                if not res.ok:
                    print('Status: {}, Reason: {}'.format(res.status_code, res.reason))
                    self.remove_proxy(cur_proxy)
                    continue
                print('Success!')
                return res
            except requests.exceptions.ProxyError as e:
                print('Proxy Error!')
                print(e)
                self.remove_proxy(cur_proxy)
            except requests.exceptions.ConnectTimeout:
                print('Timeout!')
                self.remove_proxy(cur_proxy)
            except requests.exceptions.ReadTimeout:
                print('Read Timeout!')
                self.remove_proxy(cur_proxy)
            except requests.exceptions.ConnectionError:
                print('Connection Error!')
                self.remove_proxy(cur_proxy)
        print('Proxy list empty!')
        return None


if __name__ == '__main__':
    proxy_requests = ProxyRequests()
    print(len(proxy_requests.proxies))
    result = proxy_requests.get('https://www.google.com')
    print(result.text)
    print(len(proxy_requests.proxies))
