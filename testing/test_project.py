import unittest
from webscraper_project.scraper import PerfumeScraper

class ScraperTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('setUpClass')
        cls.instance = PerfumeScraper("https://bloomperfume.co.uk/collections/perfumes")
        cls.url = "https://bloomperfume.co.uk/collections/perfumes"
        cls.stem = "https://bloomperfume.co.uk"
        pass

    @classmethod
    def tearDownClass(cls):
        cls.instance.close_webpage()
        pass

    def test_open_webpage(self):
        test_value = self.url
        self.instance.open_webpage(test_value)
        actual_value = str(self.instance.get_current_url())
        self.assertMultiLineEqual(test_value, actual_value)
        pass

    def test_search_website(self):
        test_value = self.stem + "/search?q=product"
        string = 'product'
        self.instance.search_website(string)
        actual_value = str(self.instance.get_current_url())
        self.assertMultiLineEqual(test_value, actual_value)
        pass

    def test_scroll_down(self):
        self.instance.open_webpage(self.url)
        start = float(self.instance.get_scroll_height())
        self.instance.scroll_down(4)
        end = float(self.instance.get_scroll_height())
        self.assertTrue(end > start)
        pass

    def test_scroll_up(self):
        self.instance.open_webpage(self.url)
        self.instance.scroll_down(4)
        start = float(self.instance.get_scroll_height())
        self.instance.scroll_up(4)
        end = float(self.instance.get_scroll_height())
        self.assertTrue(end < start)
        pass
    