from pydantic import BaseModel
from typing import List, Dict, Self
from bs4 import BeautifulSoup
import re
import feedparser
from tqdm import tqdm
import requests
import time

feeds = [
    "https://www.dealnews.com/c142/Electronics/?rss=1",
        "https://www.dealnews.com/c39/Computers/?rss=1",
        "https://www.dealnews.com/c238/Automotive/?rss=1",
        "https://www.dealnews.com/f1912/Smart-Home/?rss=1",
        "https://www.dealnews.com/c196/Home-Garden/?rss=1",
       ]

def extract(html_snippet: str) -> str:
    """
    Use Beautiful Soup to clean up this HTML snippet and extract useful text
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    snippet_div = soup.find('div', class_='snippet summary')
    
    if snippet_div:
        description = snippet_div.get_text(strip=True)
        description = BeautifulSoup(description, 'html.parser').get_text()
        description = re.sub('<[^<]+?>', '', description)
        result = description.strip()
    else:
        result = html_snippet
    return result.replace('\n', ' ')

class ScrapedDeal:
    """
    A class to represent a Deal retrieved from an RSS feed
    """
    category: str
    title: str
    summary: str
    url: str
    details: str
    features: str

    def __init__(self, entry: Dict[str, str]):
        """
        Populate this instance based on the provided dict
        """
        # 从传入的字典 entry 中读取标题，并赋值给实例的 title 属性
        self.title = entry['title']
        
        # 对 summary 字段进行预处理（如清洗文本或提取摘要），赋值给实例属性 summary
        self.summary = extract(entry['summary'])
        
        # 提取链接列表中的第一个链接（通常是详情页），赋值给实例的 url
        self.url = entry['links'][0]['href']
        
        # 通过 HTTP 请求下载该 URL 对应页面的 HTML 内容
        stuff = requests.get(self.url).content
        
        # 用 BeautifulSoup 解析 HTML 内容，构造 DOM 树便于后续提取
        soup = BeautifulSoup(stuff, 'html.parser')
        
        # 在页面中找到 class 为 content-section 的 div 标签，并提取纯文本内容
        content = soup.find('div', class_='content-section').get_text()
        
        # 清洗文本：去除换行符 "more"，将所有换行替换为空格，整理成整段文本
        content = content.replace('\nmore', '').replace('\n', ' ')
        
        # 如果内容中包含 "Features"，就以此为分隔符，划分出详情和功能两部分
        if "Features" in content:
            self.details, self.features = content.split("Features")
        else:
            # 否则，将全文视为 details，features 设为空字符串
            self.details = content
            self.features = ""

    def __repr__(self):
        """
        Return a string to describe this deal
        """
        return f"<{self.title}>"

    def describe(self):
        """
        Return a longer string to describe this deal for use in calling a model
        """
        return f"Title: {self.title}\nDetails: {self.details.strip()}\nFeatures: {self.features.strip()}\nURL: {self.url}"

    @classmethod
    def fetch(cls, show_progress : bool = False) -> List[Self]:
        """
        Retrieve all deals from the selected RSS feeds
        """
        # 初始化一个空列表，用于存储抓取到的 deal 实例
        deals = []
    
        # 根据是否显示进度条，选择是否将 feeds 包装成 tqdm 对象（用于显示进度）
        feed_iter = tqdm(feeds) if show_progress else feeds
    
        # 遍历所有 RSS feed 链接
        for feed_url in feed_iter:
            # 解析 RSS feed 内容，返回的是一个包含若干条目的结构（如 feed.entries）
            feed = feedparser.parse(feed_url)
    
            # 只处理每个 feed 中的前 10 个条目（避免过多请求）
            for entry in feed.entries[:10]:
                # 用每条 entry 实例化当前类（cls），并加入 deals 列表
                deals.append(cls(entry))
    
                # 为了避免对服务器造成压力，每次处理一条后休眠 0.5 秒
                time.sleep(0.5)
    
        # 返回所有已构建的 deal 实例组成的列表
        return deals


class Deal(BaseModel):
    """
    A class to Represent a Deal with a summary description
    """
    product_description: str
    price: float
    url: str

class DealSelection(BaseModel):
    """
    A class to Represent a list of Deals
    """
    deals: List[Deal]

class Opportunity(BaseModel):
    """
    A class to represent a possible opportunity: a Deal where we estimate
    it should cost more than it's being offered
    """
    deal: Deal
    estimate: float
    discount: float