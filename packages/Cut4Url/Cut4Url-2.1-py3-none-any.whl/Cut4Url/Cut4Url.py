from bs4 import BeautifulSoup
import requests

class Short:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        })
        self.get_initial_cookies()

    def get_initial_cookies(self):
        try:
            response = self.session.get('https://dev.me/products/short-url')
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error acquiring initial cookies: {e}")

    def tinycc(self, url):
        try:
            response = self.session.get('https://tiny.cc/')
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            input_element = soup.find('input', {'name': '_signature'})
            
            if input_element:
                value = input_element.get('value')
                post_headers = {
                    'accept': 'application/json',
                    'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://tiny.cc',
                    'referer': 'https://tiny.cc/',
                    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                }
                data = {
                    'url': url,
                    'custom': '',
                    'no_stats': '1',
                    '_signature': value,
                }
                response = self.session.post('https://tiny.cc/tiny/url/create', headers=post_headers, data=data)
                response.raise_for_status()
                return response.json().get("short_url")
            else:
                print("Error: '_signature' input element not found")
                return None
        except requests.RequestException as e:
            print(f"Error shortening URL with tiny.cc: {e}")
            return None

    def clck(self, url):
        try:
            response = self.session.get(f"https://clck.ru/--?url={url}")
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            print(f"Error shortening URL with clck: {e}")
            return None

    def ulvis(self, url):
        try:
            response = self.session.get(f"https://ulvis.net/api.php?url={url}")
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            print(f"Error shortening URL with ulvis: {e}")
            return None

    def isgd(self, url):
        try:
            response = self.session.get(f"https://is.gd/create.php?format=simple&url={url}")
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            print(f"Error shortening URL with isgd: {e}")
            return None

    def cleanuri(self, url):
        try:
            data = {'url': url}
            response = self.session.post('https://cleanuri.com/api/v1/shorten', data=data)
            response.raise_for_status()
            return response.json().get("result_url")
        except requests.RequestException as e:
            print(f"Error shortening URL with cleanuri: {e}")
            return None

    def abre(self, url):
        try:
            json_data = {
                'url_translation': {
                    'url': url,
                    'token': "",
                }
            }
            response = self.session.post('https://abre.ai/_/generate', json=json_data)
            response.raise_for_status()
            return response.json().get("data", {}).get("attributes", {}).get("shortenedUrl")
        except requests.RequestException as e:
            print(f"Error shortening URL with abre: {e}")
            return None

    def shorturl(self, url):
        try:
            response = self.session.post('https://www.shorturl.at/shortener.php', data={'u': url})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            clicks_link = soup.find('a', string='Total of clicks of your short URL')

            if clicks_link:
                href = clicks_link.get('href')
                if href and 'url-total-clicks.php?u=' in href:
                    short_url = href.split('url-total-clicks.php?u=')[-1]
                    return short_url
                else:
                    print("No valid short URL found.")
                    return None
            else:
                print("Link for total clicks not found.")
                return None
        except requests.RequestException as e:
            print(f"Error shortening URL with shorturl.at: {e}")
            return None

    def de(self, url):
        try:
            headers = {
                'accept': 'application/json',
                'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
                'content-type': 'application/json',
                'dnt': '1',
                'origin': 'https://dev.me',
                'priority': 'u=1, i',
                'referer': 'https://dev.me/products/short-url',
                'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                'x-api-key': 'demo-key',
            }

            json_data = {
                'domain': 'in.mt',
                'url': url,
                'suffix': '',
            }

            response = self.session.post('https://dev.me/api/module-app/v1-create-short-url', headers=headers, json=json_data)
            response.raise_for_status()
            return response.json().get("shortUrl")
        except requests.RequestException as e:
            print(f"Error creating short URL with dev.me: {e}")
            return None

    def check(self, url):
        try:
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
                'cache-control': 'max-age=0',
                'content-type': 'application/x-www-form-urlencoded',
                'dnt': '1',
                'origin': 'https://checkshorturl.com',
                'referer': 'https://checkshorturl.com/',
                'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            }

            response = self.session.post('https://checkshorturl.com/', headers=headers, data={'links': url})
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            info_div = soup.find('div', id='info')
            short_url = None
            long_url = None
            
            if info_div:
                short_url_p = info_div.find('p', string='Short URL')
                if short_url_p and short_url_p.find_next_sibling('p'):
                    short_url = short_url_p.find_next_sibling('p').text.strip()
                
                long_url_p = info_div.find('p', string='Long URL')
                if long_url_p and long_url_p.find_next_sibling('p'):
                    long_url = long_url_p.find_next_sibling('p').find('a').get('href', '').strip()
                
            return short_url, long_url
        
        except requests.RequestException as e:
            print(f"Error checking short URL: {e}")
            return None, None
