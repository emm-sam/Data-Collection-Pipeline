import json
from types import new_class
from webbrowser import Chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from time import sleep
import uuid 
import os
import json
import urllib.request
import urllib3.exceptions
import requests
import boto3
import botocore
from sqlalchemy import create_engine, table
import pandas as pd
import psycopg2
from sqlalchemy import inspect
from selenium.webdriver.chrome.options import Options

class GenericScraper:
    def __init__(self):
        self.driver = webdriver.Chrome("/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline/chromedriver")
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage') 
        # self.driver = webdriver.Chrome(options=chrome_options)
        # self.dict = {"href":['test', 'test'], "complete":['test', 'test'], "uuid":['test', 'test'], "name":['test', 'test'], "id":['123', '123'], "price":['£135', '£135'], "strength":['75ml / EdP', '75ml / EdP'], "category":['test', 'test'], "brand":['test', 'test'], "flavours":[['test', 'test'],['test', 'test']], "top notes":[['test', 'test'],['test', 'test']], "heart notes":[['test', 'test'],['test', 'test']], "base notes":[['test', 'test'],['test', 'test']], "image link":['test', 'test']}

    def open_webpage(self, url):
        self.driver.get(url)
        time.sleep(2)
        try:
            cookies_button = self.driver.find_element(By.CLASS_NAME, "accept")
            cookies_button.click()
        except NoSuchElementException:
            pass
     
    def close_webpage(self):
        self.driver.quit()

    def go_back(self):
        self.driver.back()

    def get_current_url(self):
        return self.driver.current_url

    def search_website(self, base_url:str, page_no:str):
        url = base_url + '/search?q=' + page_no
        self.driver.get(url)

    def scroll_down(self, no_seconds):
        start_time = time.time()
        while (time.time() - start_time) < no_seconds:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.DOWN)
        else:
            pass
    
    def scroll_up(self, no_seconds):
        start_time2 = time.time()
        while (time.time() - start_time2) < no_seconds:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)
        else:
            pass

    def get_full_height(self):
        total_height = str(self.driver.execute_script("return document.body.scrollHeight"))
        return total_height
        
    def get_scroll_height(self):
        current_height = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
        return current_height

    # TAKE IN WEBELEMENT
    def get_text(self, element): #5 #USED
        '''
        takes in webelement
        returns the text 
        '''
        var = element.text
        return var

    def get_attr(self, element, attribute:str): #3 #USED
        '''
        takes in webelement and attributename
        returns attribute content
        '''
        var = element.get_attribute(attribute)
        return var 

    def get_relxpathtext(self, element, relxpath:str) -> str:
        '''
        takes in a webelement and relative xpath
        returns text  
        '''
        var = element.find_element(By.XPATH, relxpath).text
        return var

    # TAKE IN XPATH
    def get_xpathtext(self, xpath:str) -> str: #USED
        '''
        takes in xpath
        returns text from that xpath
        '''
        var = self.driver.find_element(By.XPATH, xpath).text
        return var

    def get_bin(self, bin_xpath:str, bin_tag:str) -> list: #USED
        '''
        takes in container xpath and tag of the section to be looped through
        returns list of webelements 
        '''
        bin = self.driver.find_element(By.XPATH, bin_xpath)
        variable_list = bin.find_elements(By.TAG_NAME, bin_tag)
        return variable_list 

    # COMBINE NAME AND METHOD 
    def make_tuple(self, name:str, func, arg:str):
        '''
        takes in a function and its argument, and a name
        returns a tuple
        '''
        var = func(arg)
        tuple = (name, var)
        return tuple

    def loop_elements(self, list:list, func, arg:str):
        '''
        takes in a list of webelements, a function and its argument 
        loops through the list 
        returns a list of scraped outputs 
        '''
        new_list = []
        for l in list:
            if arg != 'no_arg':
                var = func(l, arg)
            else:
                var = func(l)
            new_list.append(var)
        return new_list

    def tuple_multiple(self, name:str, bin_xpath:str, bin_tag:str, func, arg:str):
        '''
        takes in xpath and name of value 
        returns a tuple? key_value pair?
        '''
        bin_tags = self.get_bin(bin_xpath=bin_xpath, bin_tag=bin_tag)
        new_list = self.loop_elements(bin_tags, func, arg)
        tuple = (name, new_list) # is this necessary 
        return tuple

    # DATA COLLECTION
    def scrape_page(self, tup_list:tuple) -> tuple:
        '''
        takes in a tuple of tuples of length 3 or 5 (must be in the required format)
        returns a dictionary with the variable name as key
        '''
        new_list = []
        for tup in tup_list:
            if len(tup) == 3:
                scraped = self.make_tuple(tup[0], tup[1], tup[2])
                new_list.append(scraped)
            elif len(tup) == 5:
                scraped = self.tuple_multiple(tup[0], tup[1], tup[2], tup[3], tup[4])
                new_list.append(scraped)
            else:
                print('Error, check your input is valid')
        new_tuple = (*new_list,) #converst list to tuple 
        dct = dict((x, y) for x, y in new_tuple) # convert tuples to dict 
        return dct

    def download_image(self, image_link:str, file_name:str, dir_path:str):
        '''
        Downloads a single image to local storage from an image link
        Args:
            image_link: url of image to be downloaded
            file_name: name of downloaded file (without filetype)
            dir_path: path of directory to be downloaded to
        '''
        try:
            self.driver.get(image_link)
            full_path = dir_path + file_name + '.jpg'
            urllib.request.urlretrieve(image_link, full_path)
        except NoSuchElementException:
            pass
    
    def href_to_url(self, base_url:str, href:str) -> str:
        full_url = base_url + href
        return full_url

    def url_to_href(self, url:str) -> str:
        split = url.split("s/")
        href = split[1]
        return href 

    # def downloads_multiple_img(self, image_list:list, dir_path:str):
    #     '''
    #     Downloads multiple images to a specified directory
    #     ?? if image link or url 
    #     '''
    #     for i in image_list:
    #         href = self.url_to_href(url=i)
    #         full_path = dir_path + href +'.jpg'
    #         if os.path.exists(full_path) == False:
    #             self.download_image(image_link=url, file_name=href, dir_path=dir_path)
    #         else:
    #             pass


class DataManipulation:
    def __init__(self):
        pass

    def open_json(self, file_path):
        '''
        Opens json file
        Args: file path
        Returns: dictionary
        '''
        with open(file_path, mode='r') as f:
            data = json.load(f)
            return data

    def dump_json(self, file_path, dict, dict_name):
        '''
        Stores dictionary as json file
        Args: 
            file_path: path to where json will be stored 
            dict: dictionary to be stored
            dict_name: name of dict, suffix with ".json"
        '''
        with open(os.path.join(file_path, dict_name), mode='w') as f:
            json.dump(dict, f)

    def uploadDirectory(self, dir_path:str):
        '''
        Uploads directory contents directly to S3 bucket
        Args: 
            dir_path: path to directory to be uploaded
        '''
        bucket = self.bucket
        for (root, dirs, files) in os.walk(dir_path):
            for file in files:
                self.s3.upload_file(os.path.join(root,file),bucket,file)

    def update_databse_rds(self, data_frame:pd.DataFrame, table_name:str):
        '''
        Uploads dataframe to specified table in AWS RDS
        Replaces existing table 
        '''
        self.engine.connect()
        data_frame.to_sql(table_name, self.engine, if_exists='replace')

    def update_table_rds(self, data_frame:pd.DataFrame, table_name:str):
        '''
        Uploads dataframe to specified table in AWS RDS
        Appends data to existing table
        '''
        self.engine.connect()
        data_frame.to_sql(table_name, con = self.engine, if_exists = 'append')

    def inspect_rds(self):
        self.engine.connect()
        # table = 'PerfumeScraper'
        table_data = pd.read_sql_table('PerfumeScraper', self.engine)
        # pd.read_sql_query('''SELECT * FROM actor LIMIT 10''', engine)
        return table_data

    def key_exists(self, mykey:str, mybucket:str):
        try:
            response = self.s3.list_objects_v2(Bucket=mybucket, Prefix=mykey)
            if response:
                for obj in response['Contents']:
                    if mykey == obj['Key']:
                        return True
        except:
            return False



class PerfumeScraper(GenericScraper, DataManipulation):

    def __init__(self):
        super().__init__()
        self.url='https://bloomperfume.co.uk/collections/perfumes'
        # self.s3 = boto3.client('s3')
        # self.bucket = input('S3 bucket name: ')
        # DATABASE_TYPE = 'postgresql'
        # DBAPI = 'psycopg2'
        # DATABASE = 'postgres'
        # ENDPOINT = input('RDS endpoint: ') 
        # USER = input('User: ')
        # PASSWORD = input('Password: ') 
        # PORT = input('Port: ')
        # self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        # self.engine.connect() 
        self.format = (
                ('name', self.get_xpathtext, '//*[@id="product-page"]/div/div[1]/div/div[1]/h1'),
                ('price', self.get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[2]/span[1]'),
                # ('sample', self.get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[2]/a[1]/span'),
                # ('token', self.get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[3]/a[1]/span'),
                ('concentration', self.get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[1]/a/span'),
                ('brand', self.get_xpathtext, '//*[@id="product-page"]/div/div[1]/div/div[1]/div/a'),
                ('description', '//*[@id="product-page"]/div/div[3]/div/div[7]', 'p', self.get_text, 'no_arg'),
                # ('style', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[5]', 'span', self.get_attr, 'data-search'),
                # ('flavours', '//*[@id="product-page"]/div/div[1]/div/div[2]', 'div', self.get_attr, 'data-search'),
                # ('top_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[1]', 'span', self.get_attr, 'data-search'),
                # ('heart_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[2]', 'span', self.get_attr, 'data-search'),
                # ('base_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[3]', 'span', self.get_attr, 'data-search'),
                # ('tags', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[4]', 'span', self.get_attr, 'data-search'),
                # ('related_perfumes', '//*[@id="product-similar"]/div/div', 'div', self.get_relxpathtext, './figure/figcaption/span[1]')
                )

    def get_urls(self, main_url:str) -> list:
        '''
        Scrapes product urls from given url
        Returns: list of urls 
        '''
        self.open_webpage(main_url)
        container = self.driver.find_element(By.XPATH, '//div[@class="products-list"]')
        prod_list = container.find_elements(By.CLASS_NAME, "product-name")
        url_list = self.loop_elements(prod_list, self.get_attr, 'href')
        return url_list

    def multiple_urls(self, no_pages:int) -> list:
        '''
        Scrapes multiple pages for urls
        Args:
            no_pages: number of pages of product
        Returns: a list of urls
        '''
        all_links = []
        for i in range(1, (no_pages+1), 1):
            paged_url = self.url + "?page=" + str(i)
            list_i = self.get_urls(paged_url)
            all_links += list_i
        return all_links

    def loop_scrape(self, url_list:list) -> list:
        '''
        Takes in a list of urls and scrapes each page
        Returns: list of individual dictionaries
        '''
        new_list = []
        for url in url_list:
            self.open_webpage(url)
            result = self.scrape_page(tup_list = self.format)
            new_list.append(result)
        return new_list



example_list = ['https://bloomperfume.co.uk/products/canvas', 'https://bloomperfume.co.uk/products/figuier-noir', 'https://bloomperfume.co.uk/products/pg20-1-sorong']

#[{'name': 'Canvas', 'price': '£110.00', 'concentration': '£110.00, 50 ml EdP', 'brand': 'Der Duft', 'description': ['', '']}, {'name': 'Figuier Noir', 'price': '£135.00', 'concentration': '£135.00, 100 ml EdP', 'brand': 'Houbigant', 'description': ['', '', '', '']}, {'name': 'PG20.1 Sorong', 'price': '£138.00', 'concentration': '£138.00, 100 ml EdP', 'brand': 'Pierre Guillaume - Parfumerie Générale', 'description': ['']}]

if __name__ == '__main__':
    myscraper = PerfumeScraper()
    myscraper.open_webpage(myscraper.url)
    # samplelist = myscraper.loop_scrape(example_list) # list containing dictionaries
    # example_dict = samplelist[0]
    # mydata = DataManipulation()
    # myscraper.inspect_rds(engine=myscraper.engine) 
    result = myscraper.loop_scrape(example_list) # list containing dictionary
    test = result.append(result)
    print(test)
    empty_dict = {}
    empty_dict['name'] = []
    empty_dict['name'].append(result[0]['name'])
    print(empty_dict)
    empty_dict['name'].append(result[1]['name'])
    print(empty_dict)
    # myscraper.dump_json('/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline/Data_Collection_Pipeline/webscraper_project', result[0], 'example.json')
    # print(myscraper.get_urls('https://bloomperfume.co.uk/collections/perfumes'))
    # pando = myscraper.inspect_rds('PerfumeScraper')
    # print(pando.head())
    myscraper.close_webpage() 
    