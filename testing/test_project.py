import unittest
from webscraper_project.scraper import PerfumeScraper

class ScraperTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('setUpClass')
        cls.instance = PerfumeScraper("https://bloomperfume.co.uk/collections/perfumes")
        cls.url = "https://bloomperfume.co.uk/collections/perfumes"
        pass

    @classmethod
    def tearDownClass(cls):
        cls.instance.close_webpage()
        pass