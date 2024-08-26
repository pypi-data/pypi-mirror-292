import unittest
from simpleynews import SimpleYNews

class TestSimpleYNews(unittest.TestCase):
    def test_ticker_news(self):
        aapl = SimpleYNews.Ticker("AAPL")
        news = aapl.news
        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)
        if news:
            self.assertIn('title', news[0])
            self.assertIn('link', news[0])
            self.assertIn('publisher', news[0])
            self.assertIn('providerPublishTime', news[0])
            self.assertIn('relatedTickers', news[0])
            self.assertEqual(news[0]['relatedTickers'], ['AAPL'])

    def test_multiple_tickers(self):
        tickers = ["AAPL", "GOOGL"]
        for ticker in tickers:
            with self.subTest(ticker=ticker):
                news = SimpleYNews.Ticker(ticker).news
                self.assertIsInstance(news, list)
                self.assertGreater(len(news), 0)
                if news:
                    self.assertIn('title', news[0])
                    self.assertIn('link', news[0])
                    self.assertIn('publisher', news[0])
                    self.assertIn('providerPublishTime', news[0])
                    self.assertIn('relatedTickers', news[0])
                    self.assertEqual(news[0]['relatedTickers'], [ticker])

    def test_news_caching(self):
        aapl = SimpleYNews.Ticker("AAPL")
        news1 = aapl.news
        news2 = aapl.news
        self.assertIs(news1, news2)  # Check if the same object is returned (cached)

if __name__ == '__main__':
    unittest.main()