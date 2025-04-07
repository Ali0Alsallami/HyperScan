import aiohttp
import asyncio
import re
from urllib.parse import urljoin
import logging

class AdvancedCrawler:
    def __init__(self, base_url, max_depth=3, proxy=None):  # تغيير proxies إلى proxy
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
        self.proxy = proxy  # نستخدم proxy كسلسلة نصية واحدة (مثل "http://proxy:port")
        self.results = {
            'urls': [],
            'emails': [],
            'js_files': [],
            'api_endpoints': []
        }

    async def fetch(self, session, url, depth):
        if depth > self.max_depth or url in self.visited:
            return
        self.visited.add(url)

        try:
            # تمرير الوكيل لكل طلب بدلاً من الجلسة
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5), proxy=self.proxy) as response:
                if response.status == 200:
                    html = await response.text()
                    self.results['urls'].append(url)
                    self.extract_emails(html)
                    self.extract_js_and_endpoints(html)

                    # استخراج الروابط الداخلية باستخدام regex بسيط
                    links = re.findall(r'href=["\'](.*?)["\']', html)
                    for link in links:
                        new_url = urljoin(url, link)
                        if self.base_url in new_url:
                            await self.fetch(session, new_url, depth + 1)
        except Exception as e:
            logging.error(f"Crawler error on {url}: {e}")

    def extract_emails(self, html):
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', html)
        self.results['emails'].extend(emails)

    def extract_js_and_endpoints(self, html):
        js_files = re.findall(r'src=["\'](.*?\.js)["\']', html)
        self.results['js_files'].extend(js_files)
        endpoints = re.findall(r'["\'](/api/[^"\']+)["\']', html)
        self.results['api_endpoints'].extend(endpoints)

    async def start(self):
        async with aiohttp.ClientSession(trust_env=True) as session:
            await self.fetch(session, self.base_url, 1)
        return self.results
