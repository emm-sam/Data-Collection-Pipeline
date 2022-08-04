import boto3
import botocore
import os
import pandas as pd
import psycopg2
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy import create_engine, table
from sqlalchemy import inspect
from time import sleep
from webscraper_2.base_scraper import GenericScraper
from webscraper_2.data_manip import DataManipulation

class PerfumeScraper(GenericScraper, DataManipulation):
    def __init__(self, creds: str='/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline/Data_Collection_Pipeline/creds/rds_creds.yaml'):
        super().__init__()
        self.url='https://bloomperfume.co.uk/collections/perfumes'
        self.s3 = boto3.client('s3')
        self.path = os.getcwd()
        # DATABASE_TYPE=os.environ.get('DATABASE_TYPE')
        # DBAPI=os.environ.get('DBAPI')
        # USER=os.environ.get('USER')
        # PASSWORD=os.environ.get('RDS_PASSWORD')
        # ENDPOINT=os.environ.get('ENDPOINT')
        # PORT=os.environ.get('PORT')
        # DATABASE=os.environ.get('DATABASE')
        # BUCKET=os.environ.get('BUCKET')
        # self.bucket = BUCKET

        with open(creds, 'r') as f:
            creds = yaml.safe_load(f)
        DATABASE_TYPE= creds['DATABASE_TYPE']
        DBAPI= creds['DBAPI']
        USER= creds['USER']
        PASSWORD= creds['PASSWORD']
        ENDPOINT= creds['ENDPOINT']
        PORT= creds['PORT']
        DATABASE= creds['DATABASE']
        self.bucket = 'imagebucketaic'

        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        self.engine.connect() 
        self.format = (
                ('name', self.get_xpathtext, '//*[@id="product-page"]/div/div[1]/div/div[1]/h1'),
                ('price', self.get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[2]/span[1]'),
                ('sample', self.get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[2]/a[1]/span'),
                ('token', self.get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[3]/a[1]/span'),
                ('concentration', self.get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[1]/a/span'),
                ('brand', self.get_xpathtext, '//*[@id="product-page"]/div/div[1]/div/div[1]/div/a'),
                ('description', '//*[@id="product-page"]/div/div[3]/div/div[7]', 'p', self.get_text, 'no_arg'),
                # ('style', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[5]', 'span', self.get_attr, 'data-search'),
                ('flavours', '//*[@id="product-page"]/div/div[1]/div/div[2]', 'div', self.get_attr, 'data-search'),
                ('top_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[1]', 'span', self.get_attr, 'data-search'),
                ('heart_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[2]', 'span', self.get_attr, 'data-search'),
                ('base_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[3]', 'span', self.get_attr, 'data-search'),
                # ('tags', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[4]', 'span', self.get_attr, 'data-search'),
                ('related_perfumes', '//*[@id="product-similar"]/div/div', 'div', self.get_relxpathtext, './figure/figcaption/span[1]')
                )

    def uploadDirectory(self, dir_path : str):
        '''
        Uploads directory contents directly to S3 bucket
        Args: 
            dir_path: path to directory to be uploaded
        '''
        bucket = self.bucket
        for (root, dirs, files) in os.walk(dir_path):
            for file in files:
                self.s3.upload_file(os.path.join(root,file),bucket,file)

    def update_databse_rds(self, data_frame : pd.DataFrame, table_name : str):
        '''
        Uploads dataframe to AWS RDS, replaces table if exists
        Args:
            data_frame: dataframe to be uploaded 
            table_name: RDS table name 
        '''
        # self.engine.connect()
        data_frame.to_sql(table_name, self.engine, if_exists='replace')
        
    def update_table_rds(self, data_frame : pd.DataFrame, table_name : str):
        '''
        Uploads dataframe to AWS RDS, appends to table if exists
        Args:
            data_frame: dataframe to be uploaded 
            table_name: RDS table name 
        '''
        # self.engine.connect()
        data_frame.to_sql(table_name, con = self.engine, if_exists = 'append')
        print('Adding new perfumes to RDS database...')

    def inspect_rds(self, table_name : str):
        '''
        Reads RDS data as a dataframe 
        Args: table_name: table to be inspected
        Returns: dataframe of all data on RDS table
        '''
        table_data = pd.read_sql_table(table_name, self.engine)
        return table_data

    def key_exists(self, mykey : str, mybucket : str):
        '''
        Checks whether an object exists in a specified S3 bucket
        Args: 
            mykey: name of file to be checked 
            mybucket: name of S3 bucket
        Returns: boolean value whether the file exists or not
        '''
        try:
            response = self.s3.list_objects_v2(Bucket=mybucket, Prefix=mykey)
            if response:
                for obj in response['Contents']:
                    if mykey == obj['Key']:
                        return True
        except:
            return False

    def href_to_url(self, base_url : str, href : str) -> str:
        '''
        Creates full url from base_url and href
        '''
        return base_url + href

    def url_to_href(self, url : str) -> str:
        '''
        Converts full url to product href (unique identifier)
        '''
        split = url.split("s/")
        return split[1]

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

    def bloom_href(self, href : str) -> str:
        '''
        Creates full url from product href
        '''
        return self.href_to_url(base_url='https://bloomperfume.co.uk/products/', href=href)

    def get_urls(self, main_url : str) -> list:
        '''
        Scrapes product urls from main product page url
        Args: main_url: main product page url
        Returns: list of urls 
        '''
        self.open_webpage(main_url)
        try:
            container = self.driver.find_element(By.XPATH, '//div[@class="products-list"]')
            prod_list = container.find_elements(By.CLASS_NAME, "product-name")
            url_list = self.loop_elements(prod_list, self.get_attr, 'href')
        except NoSuchElementException:
            url_list = ['None', 'None']
            print('Could not find urls')
        return url_list

    def multiple_urls(self, no_pages : int) -> list:
        '''
        Scrapes multiple pages for urls
        Args:
            no_pages: number of pages of product to loop through
        Returns: a list of product urls
        '''
        all_links = []
        for i in range(1, (no_pages+1), 1):
            paged_url = self.url + "?page=" + str(i)
            list_i = self.get_urls(paged_url)
            all_links += list_i
        return all_links

    def loop_scrape(self, url_list : list) -> list:
        '''
        Takes in a list of urls and scrapes each page
        Args: url_list: list of product urls to be scraped
        Returns: list of individual dictionaries
        '''
        dict_list = []
        for url in url_list:
            self.open_webpage(url)
            result = self.scrape_page(tup_list = self.format)
            result['url'] = url
            result['href'] = self.url_to_href(url=url)
            # result['image_link'] = self.get_xpathattr('/html/body/div[4]/main/div[2]/div/div[2]/div/div[2]/div/div/img', 'src')
            dict_list.append(result)
        return dict_list

    def run_scraper_local(self, no_pages : int):
            '''
            Compares product data stored locally to newly scraped urls. 
            Only scrapes from products not present in the database. 
            Creates database if it does not exist already. 
            '''
            new_urls = self.multiple_urls(no_pages)
            new_hrefs = self.url_href_list(new_urls)
            new_data = self.loop_scrape(new_urls)
            new_dict = self.list_to_dict(new_data)
            self.dump_json(self.path, new_dict, 'new_dict.json')
            print("Storing data locally...")

example_list = ['https://bloomperfume.co.uk/products/canvas', 'https://bloomperfume.co.uk/products/figuier-noir', 'https://bloomperfume.co.uk/products/pg20-1-sorong']
example_listfdicts= [{'name': 'Canvas', 'price': '£110.00', 'concentration': '£110.00, 50 ml EdP', 'brand': 'Der Duft', 'description': ['', '']}, {'name': 'Figuier Noir', 'price': '£135.00', 'concentration': '£135.00, 100 ml EdP', 'brand': 'Houbigant', 'description': ['', '', '', '']}, {'name': 'PG20.1 Sorong', 'price': '£138.00', 'concentration': '£138.00, 100 ml EdP', 'brand': 'Pierre Guillaume - Parfumerie Générale', 'description': ['']}]

if __name__ == '__main__':
    myscraper = PerfumeScraper()
    myscraper.open_webpage(myscraper.url)
    samplelist = myscraper.loop_scrape(example_list) # list containing dictionaries
    print(samplelist)
    # example_dict = samplelist[0]
    # mydata = DataManipulation()
    # myscraper.inspect_rds(engine=myscraper.engine) 
    # result = myscraper.loop_scrape(example_list) # list containing dictionary
    # myscraper.dump_json('/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline/Data_Collection_Pipeline/webscraper_project', result[0], 'example.json')
    # print(myscraper.get_urls('https://bloomperfume.co.uk/collections/perfumes'))
    # pando = myscraper.inspect_rds('PerfumeScraper')
    # print(pando.head())

    # url_list = myscraper.multiple_urls(no_pages=2) - tested 20/6
    # list_dict = myscraper.loop_scrape(url_list=url_list) tested 20/6
    # first_40 = myscraper.list_to_dict(list_dict) tested 20/6
    # myscraper.dump_json('/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline', first_40, 'FIRST_40.json') tested 20/6
    myscraper.close_webpage() 

    