from typing import Optional
import re
import time
import requests
from bs4 import BeautifulSoup

class Bug:
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.domain: Optional[str] = self.get_domain(url)
        self.response: Optional[requests.Response] = None
        self.soup: Optional[BeautifulSoup] = None

    def get_domain(self, url: str) -> Optional[str]:
        regex: str = r'(https?://[^/]+)'
        domain: Optional[re.Match] = re.search(regex, url)
        if domain:
            return domain.group(1)
        return None

    def setup(self, headers: dict) -> str:
        time.sleep(3)
        self.response = requests.get(self.url, headers=headers)
        if self.response.status_code == 200:
            self.soup = BeautifulSoup(self.response.text, "html.parser")
            return '設置成功'
        else:
            raise Exception(f"設置失敗，無法獲取URL: {self.url}，狀態碼: {self.response.status_code}")