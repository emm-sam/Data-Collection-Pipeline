from selenium import webdriver
import time
from time import sleep
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class PerfumeScraper: 
   
    def __init__(self, url): 
        self.driver = webdriver.Chrome("/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline/chromedriver") 
        self.url = url

    def open_webpage(self, url):
        self.driver.get(url)
        time.sleep(2)
        try:
            cookies_button = self.driver.find_element(By.CLASS_NAME, "accept")
            cookies_button.click()
        except NoSuchElementException:
            pass


if __name__ == '__main__':      
    my_scraper = PerfumeScraper("https://bloomperfume.co.uk/collections/perfumes")