import csv
import json
import os
import pandas as pd
import time
from csv import DictWriter, DictReader
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class PerfumeScraper: 
    def __init__(self, url):
        self.url = url
        self.path = os.getcwd()
        self.fieldnames = ['url', 'href', 'name', 'brand', 'description', 'category', 'badges', 'prices', 'topnotes', 'midnotes', 'basenotes', 'Notes', 'Tags', 'Style', '', 'similar_perfumes']
        self.table = 'PerfumeScraper'
        self.data_path = self.path + '/data'    
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        
    # FOR WEBSITE NAVIGATION

    def open_webpage(self, url : str):
        '''
        Takes in url and opens the webpage
        '''
        self.driver.get(url)
        time.sleep(2)
        try:
            cookies_button = self.driver.find_element(By.CLASS_NAME, "accept")
            cookies_button.click()
        except NoSuchElementException:
            pass

    def close_webpage(self):
        '''
        Closes browser
        '''
        self.driver.quit()

    # COLLECTING DATA FROM THE WEBSITE

    def get_current_url(self) -> str:
        '''
        Returns current url
        '''
        return self.driver.current_url

    def get_links(self, url : str) -> list:#tested 26/04/23
        '''
        Scrapes product urls from webpage
        Args: 'url': full product list webpage
        Returns: list of urls scraped from the webpage
        '''
        self.open_webpage(url)
        time.sleep(1)
        try:
            product_container = self.driver.find_element(By.XPATH, '//div[@class="products-list"]')
            prod_list = product_container.find_elements(By.CLASS_NAME, "product-name")
            link_list = [] 
            for p in prod_list:
                href = p.get_attribute("href")
                link_list.append(href)
            return link_list
        except NoSuchElementException:
            return []
        
    def get_multiple_links(self, start_page : int, number_pages : int) -> list:#tested 26/04/23
        '''
        Scrapes urls from multiple product pages
        Args: number_pages: number of pages to be scraped for urls
        Returns: a list of product urls 
        '''
        all_links = []
        for i in range(start_page, (number_pages+1), 1):
            paged_url = self.url + "?page=" + str(i)
            list_i = self.get_links(paged_url)
            all_links += list_i
        return all_links

    def scrape_title(self): #checked on 26/04/23
        try:
            element = self.driver.find_element(By.CLASS_NAME,'product-name')
            # output = element.get_attribute('name') #itemprop?
            output = element.text
            return output
        except NoSuchElementException:
            return None

    def scrape_brand(self): #checked on 26/04/23 
        try:
            element = self.driver.find_element(By.CLASS_NAME,'product-brand')
            output = element.find_element(By.TAG_NAME, 'a').text
            return output
        except NoSuchElementException:
            return None

    def scrape_oneliner(self): #checked on 26/04/23 
        try:
            element = self.driver.find_element(By.CLASS_NAME,'product-promo-description')
            output = element.find_element(By.TAG_NAME, 'i').text
            return output
        except NoSuchElementException:
            return None

    def scrape_badges(self):
        try:
            product_badges = self.driver.find_element(By.CLASS_NAME, 'product-badges')
            badges = product_badges.find_elements(By.TAG_NAME, 'a')
            badge_list = []
            for b in badges:
                badge_list.append(b.text)
            return badge_list
        except NoSuchElementException:
            return None       

    def scrape_prices(self):#tested 26/04/23
        try:
            variant_list = self.driver.find_elements(By.CLASS_NAME, 'variant__info')
            text_list = []
            for v in variant_list:
                text_list.append(v.text)
            return text_list
        except NoSuchElementException:
            return None

    def scrape_flavours(self):#tested 26/04/23
        try:
            flavour = self.driver.find_element(By.XPATH, '/html/body/div[4]/main/div[2]/div/div[1]/div/div[2]')
            flav_list_elements = flavour.find_elements(By.TAG_NAME, 'span')
            flav_list = []
            for f in flav_list_elements:
                flav_list.append(f.text)
            return flav_list
        except NoSuchElementException:
            return None

    def scrape_topnotes(self):#tested 26/04/23
        try:
            note = self.driver.find_element(By.CLASS_NAME, 'product-ingredients__top')
            notes = note.find_elements(By.TAG_NAME, "span")
            notes_list = []
            for n in notes:
                if n:
                    notes_list.append(n.text)
            return list(set(notes_list))
        except NoSuchElementException:
            return None

    def scrape_heartnotes(self):#tested 26/04/23
        try:
            note = self.driver.find_element(By.CLASS_NAME, 'product-ingredients__heart')
            notes = note.find_elements(By.TAG_NAME, "span")
            notes_list = []
            for n in notes:
                if n:
                    notes_list.append(n.text)
            return list(set(notes_list))
        except NoSuchElementException:
            return None

    def scrape_basenotes(self):#tested 26/04/23
        try:
            note = self.driver.find_element(By.CLASS_NAME, 'product-ingredients__base')
            notes = note.find_elements(By.TAG_NAME, "span")
            notes_list = []
            for n in notes:
                if n:
                    notes_list.append(n.text)
            return list(set(notes_list))
        except NoSuchElementException:
            return None

    def scrape_ingredients(self):#tested 26/04/23
        try:
            buckets = self.driver.find_elements(By.CLASS_NAME, 'product-ingredients__all')
            altogether = {}
            for b in buckets:
                result = self.scrape_ingred(b)
                if result != '':
                    altogether.update(result)
            return altogether #dictionary
        except NoSuchElementException:
            return None

    def scrape_ingred(self, element):#tested 26/04/23
        try:
            element_dict = {}
            section_name = element.find_element(By.TAG_NAME, 'strong').text #string
            spans = element.find_elements(By.TAG_NAME, "span")
            spans_list = []
            for s in spans:
                if s:
                    spans_list.append(s.text)
            clean = list(set(spans_list))
            element_dict[section_name] = clean  
            return element_dict    
        except NoSuchElementException:
            return None
    
    # def scrape_description(self):
    #     try:
    #         description = self.driver.find_element(By.CLASS_NAME, 'product-description desktop--hide')
    #         paragraph = description.find_elements(By.TAG_NAME, 'p')
    #         # p = paragraph.get_attribute('text()')
    #         # description = []
    #         # for o in paragraphs:
    #         #     description.append(o.text)
    #         # return description
    #         return paragraph
    #     except NoSuchElementException:
    #         return None

    def scrape_similar_items(self): #tested 26/04/23
        try:
            bucket = self.driver.find_element(By.CLASS_NAME, 'product-similar__items')
            tag = bucket.find_elements(By.TAG_NAME, 'a')
            href_list = []
            for t in tag:
                url = t.get_attribute("href")
                href = self.url_to_href(url)
                href_list.append(href)
            return href_list
        except NoSuchElementException:
            return None

    def build_dictionary(self, product_url): #tested 26/04/23
        self.open_webpage(product_url)
        d = {}
        current_url = self.driver.current_url
        d['url'] = current_url
        d['href'] = self.url_to_href(current_url)
        d['name'] = self.scrape_title()
        d['brand'] = self.scrape_brand()
        d['description'] = self.scrape_oneliner()
        d['category'] = self.scrape_flavours()
        d['badges'] = self.scrape_badges()
        d['prices'] = self.scrape_prices()
        d['topnotes'] = self.scrape_topnotes()
        d['midnotes'] = self.scrape_heartnotes()
        d['basenotes'] = self.scrape_basenotes()
        ingredients = self.scrape_ingredients()
        d.update(ingredients)
        if 'Notes' not in d:
            d['Notes'] = None
        if 'Tags' not in d:
            d['Tags'] = None
        if 'Style' not in d:
            d['Style'] = None
        d['similar_perfumes'] = self.scrape_similar_items()
        # perfume_dataframe = pd.DataFrame.from_dict(d, orient='index')
        # perfume_dataframe = perfume_dataframe.transpose()
        return(d)

    def list_ofdicts(self, url_list): #tested 26/04/23
        # loops through a list of urls, creates product dictionary, output is a list of dictionaries
        if len(url_list) >= 1:
            list_of_dicts = [] 
            for url in url_list:
                product_dict = self.build_dictionary(url)
                list_of_dicts.append(product_dict)
            return list_of_dicts
        else:
            return [{}]

    def list_dicts_to_csv_empty(self, list_of_dicts, csv_path):
        field_names = self.fieldnames
        if len(list_of_dicts) >= 1:
            with open(csv_path, 'a') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                dictwriter_object.writeheader()
                for d in list_of_dicts:
                    dictwriter_object.writerow(d)
                f_object.close()
        else:
            pass

    def compare_hrefs(self, new_urls : list, csv_hrefs : list):
        scrape_hrefs = self.url_href_list(new_urls) #scraped urls
        if len(scrape_hrefs) > 0:
            unscraped_urls = []
            for href in scrape_hrefs:
                if href not in csv_hrefs:
                    url = self.bloom_href(href)
                    unscraped_urls.append(url)
            return unscraped_urls
        else:
            return []

    def list_dicts_to_csv_not_empty(self, list_of_dicts, csv_path):
        field_names = self.fieldnames
        if len(list_of_dicts) >= 1:
            with open(csv_path, 'a') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                for d in list_of_dicts:
                    dictwriter_object.writerow(d)
                f_object.close()
        else:
            pass

    def csv_col(self, csv_path):
        '''
        Returns a list of hrefs stored in the csv
        '''
        try:
            with open(csv_path, 'r') as csv_filename:
                csv_reader = csv.reader(csv_filename)
                list_of_csv = list(csv_reader)
                href_list = []
                for l in list_of_csv:
                    href_list.append(l[1])
                return href_list
        except:
            pass

    # future: function - turns a list of dictionaries into a nested json file 

    def concat_dataframe(self, d1, d2):
        result = pd.concat([d1,d2])
        result = result.reset_index(drop=True)
        return result

    def dump_json(self, filepath : str, dict : dict, dict_name : str):
        '''
        Stores ditionary as json file
        Args:
            filepath: path to the directory to store the json
            dict: dictionary to be stored
            dict_name: name of json file (must end .json)
        '''
        with open(os.path.join(filepath, dict_name), mode='w') as f:
            json.dump(dict, f)

    def open_json(self, file_path : str) -> dict:
        '''
        Opens json file to dictionary 
        Args: filepath: path to json file to be uploaded
        '''
        with open(file_path, mode='r') as f:
            data = json.load(f)
            return data

    def url_to_href(self, url : str) -> str:
        '''
        Converts bloom product url to href
        '''
        split = url.split("s/")
        return split[1]

    def href_to_url(self, base_url : str, href : str) -> str:
        '''
        Adds href to a given url
        '''
        return base_url + href

    def bloom_href(self, href : str) -> str:
        '''
        Creates full url from product href
        '''
        return self.href_to_url(base_url='https://bloomperfume.co.uk/products/', href=href)

    def url_href_list(self, urls : str) -> list:
        '''
        Takes list of urls
        Returns list of hrefs 
        '''
        scraped_href_list = []
        for x in urls:
            href = self.url_to_href(x)
            scraped_href_list.append(href)
        return scraped_href_list

    # INTEGRATING THE ABOVE

    def run_scraper(self, start_from, no_pages, csv_path, existing_json_path=False):
        scraped_urls_list = self.get_multiple_links(start_from, no_pages) # 49 maximum
        csv_href_list = self.csv_col(csv_path)
        if csv_href_list == []:
            list_of_product_dict = self.list_ofdicts(scraped_urls_list)
            self.list_dicts_to_csv_empty(list_of_product_dict, csv_path)
        else:
            urls_not_in_csv = self.compare_hrefs(scraped_urls_list, csv_href_list)
            list_of_new_product_dict = self.list_ofdicts(urls_not_in_csv)
            self.list_dicts_to_csv_not_empty(list_of_new_product_dict, csv_path)

if __name__ == '__main__':      
    my_scraper = PerfumeScraper("https://bloomperfume.co.uk/collections/perfumes")
    my_scraper.run_scraper(35,49,'/Users/emmasamouelle/Desktop/Scratch/bloom_2023/perfume.csv')
    print("--------------")
    my_scraper.close_webpage()