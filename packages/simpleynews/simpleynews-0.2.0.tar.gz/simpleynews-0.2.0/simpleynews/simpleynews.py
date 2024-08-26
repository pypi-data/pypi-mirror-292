import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import logging
import uuid

class Ticker:
    def __init__(self, symbol):
        self.symbol = symbol
        self.logger = self._setup_logging()
        self._news_cache = None

    @staticmethod
    def _setup_logging():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    @property
    def news(self):
        if self._news_cache is None:
            self._news_cache = self._scrape_news()
        return self._news_cache

    def _parse_relative_time(self, time_str):
        current_time = datetime.now(pytz.UTC)
        if 'days ago' in time_str:
            days = int(time_str.split()[0])
            return current_time - timedelta(days=days)
        elif 'hours ago' in time_str:
            hours = int(time_str.split()[0])
            return current_time - timedelta(hours=hours)
        elif 'minutes ago' in time_str:
            minutes = int(time_str.split()[0])
            return current_time - timedelta(minutes=minutes)
        else:
            return current_time

    def _scrape_news(self):
        url = f"https://finance.yahoo.com/quote/{self.symbol}/news"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.logger.info(f"Successfully fetched the page for {self.symbol}")
        except requests.RequestException as e:
            self.logger.error(f"Error fetching the page for {self.symbol}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        news_elements = soup.select('li section.yf-1044anq') or soup.select('ul li section')

        if not news_elements:
            self.logger.warning(f"No news items found for {self.symbol}")
            return []
        
        self.logger.info(f"Found {len(news_elements)} news items for {self.symbol}")

        for item in news_elements:
            try:
                news_item = self._parse_news_item(item)
                if news_item:
                    news_items.append(news_item)
            except Exception as e:
                self.logger.error(f"Error parsing a news item: {e}")
        
        return news_items

    def _parse_news_item(self, item):
        title_elem = item.select_one('h3.yf-1044anq') or item.select_one('h3')
        link_elem = item.select_one('a')
        
        if title_elem and link_elem:
            title = title_elem.text.strip()
            href = 'https://finance.yahoo.com' + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href']
            
            footer = item.select_one('div.yf-da5pxu') or item.select_one('div[data-test="story-meta"]')
            if footer:
                footer_text = footer.text.strip()
                parts = footer_text.split('\u2022')
                publisher = parts[0].strip()
                timestamp_str = parts[-1].strip() if len(parts) > 1 else "Unknown"
                date = self._parse_relative_time(timestamp_str)
            else:
                self.logger.warning("Footer not found, using default values")
                publisher = "Unknown"
                date = datetime.now(pytz.UTC)

            news_item = {
                'uuid': str(uuid.uuid4()),
                'title': title,
                'link': href,
                'publisher': publisher,
                'providerPublishTime': int(date.timestamp()),
                'type': 'STORY',
                'relatedTickers': [self.symbol],
                'thumbnail': {},
                'summary': ''
            }
            self.logger.info(f"Successfully parsed news item: {title}")
            return news_item
        else:
            self.logger.warning("Title or link element not found, skipping this item")
            return None

class SimpleYNews:
    @staticmethod
    def Ticker(symbol):
        return Ticker(symbol)

# Example usage
if __name__ == "__main__":
    aapl = SimpleYNews.Ticker("AAPL")
    news = aapl.news
    for item in news:
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Publisher: {item['publisher']}")
        print(f"Publish Time: {datetime.fromtimestamp(item['providerPublishTime'], tz=pytz.UTC)}")
        print(f"Type: {item['type']}")
        print(f"Related Tickers: {item['relatedTickers']}")
        print(f"UUID: {item['uuid']}")
        print("---")