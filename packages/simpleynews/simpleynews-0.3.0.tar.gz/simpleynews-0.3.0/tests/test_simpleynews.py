import unittest
from simpleynews import SimpleYNews
from datetime import datetime
import pytz

class TestSimpleYNews(unittest.TestCase):
    def test_ticker_news(self):
        aapl = SimpleYNews.Ticker("AAPL")
        news = aapl.news
        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)
        if news:
            self.assertIn('uuid', news[0])
            self.assertIn('title', news[0])
            self.assertIn('link', news[0])
            self.assertIn('publisher', news[0])
            self.assertIn('providerPublishTime', news[0])
            self.assertIn('type', news[0])
            self.assertIn('relatedTickers', news[0])
            self.assertIn('thumbnail', news[0])
            self.assertIn('summary', news[0])
            
            self.assertIsInstance(news[0]['uuid'], str)
            self.assertIsInstance(news[0]['title'], str)
            self.assertIsInstance(news[0]['link'], str)
            self.assertIsInstance(news[0]['publisher'], str)
            self.assertIsInstance(news[0]['providerPublishTime'], float)
            self.assertEqual(news[0]['type'], 'STORY')
            self.assertEqual(news[0]['relatedTickers'], ['AAPL'])
            self.assertIsInstance(news[0]['thumbnail'], dict)
            self.assertIsInstance(news[0]['summary'], str)

    def test_multiple_tickers(self):
        tickers = ["AAPL", "GOOGL"]
        for ticker in tickers:
            with self.subTest(ticker=ticker):
                news = SimpleYNews.Ticker(ticker).news
                self.assertIsInstance(news, list)
                self.assertGreater(len(news), 0)
                if news:
                    self.assertIn('uuid', news[0])
                    self.assertIn('title', news[0])
                    self.assertIn('link', news[0])
                    self.assertIn('publisher', news[0])
                    self.assertIn('providerPublishTime', news[0])
                    self.assertIn('type', news[0])
                    self.assertIn('relatedTickers', news[0])
                    self.assertEqual(news[0]['relatedTickers'], [ticker])

    def test_news_caching(self):
        aapl = SimpleYNews.Ticker("AAPL")
        news1 = aapl.news
        news2 = aapl.news
        self.assertIs(news1, news2)  # Check if the same object is returned (cached)

    def test_publish_time_format(self):
        aapl = SimpleYNews.Ticker("AAPL")
        news = aapl.news
        if news:
            publish_time = news[0]['providerPublishTime']
            self.assertIsInstance(publish_time, float)
            # Check if the timestamp is recent (within the last week)
            self.assertLess(datetime.now(pytz.UTC).timestamp() - publish_time, 7 * 24 * 60 * 60)

if __name__ == '__main__':
    unittest.main()