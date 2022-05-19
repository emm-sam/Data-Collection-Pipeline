from selenium import webdriver

class PerfumeScraper: 
   
    def __init__(self, url): 
        self.driver = webdriver.Chrome("/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline/chromedriver") 
        self.url = url


if __name__ == '__main__':      
    my_scraper = PerfumeScraper("https://bloomperfume.co.uk/collections/perfumes")