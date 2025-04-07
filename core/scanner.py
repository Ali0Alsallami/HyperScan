import aiohttp
import asyncio
import logging
from urllib.parse import urljoin

class DirectoryScanner:
    def __init__(self, base_url, wordlist_path, proxy=None):  # تغيير proxies إلى proxy
        self.base_url = base_url.rstrip('/')
        self.wordlist = self.load_wordlist(wordlist_path)
        self.proxy = proxy  # نستخدم proxy كسلسلة نصية واحدة
        self.found = []
        self.vuln_files = {
            ".env": "Potentially exposed environment variables",
            "backup.sql": "Database backup leak",
            "config.php": "Configuration file exposure"
        }

    def load_wordlist(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f]
        except FileNotFoundError:
            raise Exception(f"Wordlist file '{path}' not found")

    async def check_path(self, session, path, total_paths, processed):
        target = urljoin(self.base_url, path)
        try:
            # تمرير الوكيل لكل طلب
            async with session.get(target, timeout=aiohttp.ClientTimeout(total=5), proxy=self.proxy) as response:
                status = response.status
                content = await response.text()
                size = len(content)
                if status < 400:
                    extra = ""
                    for vuln_file, desc in self.vuln_files.items():
                        if vuln_file in target:
                            extra += f" | Warning: {desc}"
                    self.found.append({
                        'url': target,
                        'status': status,
                        'size': size,
                        'extra': extra
                    })
        except Exception as e:
            logging.error(f"Scanner error on {target}: {e}")
        processed[0] += 1
        print(f"\r[*] Progress: {processed[0]}/{total_paths} ({processed[0]/total_paths*100:.1f}%)", end="")

    async def run(self, max_concurrent=30):
        total_paths = len(self.wordlist)
        processed = [0]  # متغير مشترك لتتبع التقدم
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=max_concurrent), trust_env=True) as session:
            tasks = [self.check_path(session, path, total_paths, processed) for path in self.wordlist]
            await asyncio.gather(*tasks)
        return sorted(self.found, key=lambda x: x['status'])
