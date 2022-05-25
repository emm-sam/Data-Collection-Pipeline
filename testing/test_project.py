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

    def test_go_back(self):
        self.instance.open_webpage(self.url)
        test_url = self.stem + '/products/ibiza-nights'
        self.instance.open_webpage(test_url)
        self.instance.go_back()
        original_page = self.instance.get_current_url()
        self.assertTrue(original_page == self.url)

    def test_clean_list(self):
        expected_value = ['one', 'two', 'three']
        list = ['one', None, 'two', None, 'three']
        actual_value = self.instance.clean_list(list)
        self.assertEqual(expected_value, actual_value)

    def test_get_links(self):
        actual_value = self.instance.get_links(self.url)
        self.assertTrue(type(actual_value) == list)
        self.assertTrue(type(actual_value[0]) == str)
        self.assertTrue(len(actual_value) >= 20)
        for a in actual_value:
            split = a.split("/p") #may have to change this 
            self.assertMultiLineEqual(split[0], self.stem)

    def test_get_multiple_links(self):
        actual_value = self.instance.get_multiple_links(2)
        self.assertTrue(type(actual_value) == list)
        self.assertTrue(type(actual_value[0]) == str)
        self.assertTrue(len(actual_value) > 20)
        for a in actual_value:
            split = a.split("/p")
            self.assertMultiLineEqual(split[0], self.stem)
    
    def test_scrape_product(self):
        test_url = self.stem + "/products/ibiza-nights"
        actual_value = self.instance.scrape_product(test_url)
        self.assertTrue(type(actual_value) == dict)
        # self.assertTrue(len(actual_value.keys()) == 13)
        self.assertTrue(type(actual_value['href']) == str)
        self.assertMultiLineEqual(actual_value['href'], "ibiza-nights")
        