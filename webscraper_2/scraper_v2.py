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
    def __init__(self, bucket : str, table : str):
        super().__init__()
        self.url='https://bloomperfume.co.uk/collections/perfumes'
        self.path = os.getcwd()
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.table = table
        self.format = (
                ('name', self._get_xpathtext, '//*[@id="product-page"]/div/div[1]/div/div[1]/h1'),
                ('price', self._get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[2]/span[1]'),
                ('sample', self._get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[2]/a[1]/span'),
                ('token', self._get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[3]/a[1]/span'),
                ('concentration', self._get_xpathtext, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[1]/a/span'),
                ('brand', self._get_xpathtext, '//*[@id="product-page"]/div/div[1]/div/div[1]/div/a'),
                ('description', '//*[@id="product-page"]/div/div[3]/div/div[7]', 'p', self._get_text, 'no_arg'),
                # ('style', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[5]', 'span', self._get_attr, 'data-search'),
                # ('flavours', '//*[@id="product-page"]/div/div[1]/div/div[2]', 'div', self._get_attr, 'data-search'),
                ('top_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[1]', 'span', self._get_attr, 'data-search'),
                ('heart_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[2]', 'span', self._get_attr, 'data-search'),
                ('base_notes', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[3]', 'span', self._get_attr, 'data-search'),
                # ('tags', '//*[@id="product-page"]/div/div[3]/div/div[6]/div[4]', 'span', self._get_attr, 'data-search'),
                ('related_perfumes', '//*[@id="product-similar"]/div/div', 'div', self._get_relxpathtext, './figure/figcaption/span[1]')
                )

    def __uploadDirectory(self, dir_path : str):
        '''
        Uploads directory contents directly to S3 bucket
        Args: 
            dir_path: path to directory to be uploaded
        '''

        bucket = self.bucket
        for (root, dirs, files) in os.walk(dir_path):
            for file in files:
                self.s3.upload_file(os.path.join(root,file),bucket,file)

    def __update_databse_rds(self, data_frame : pd.DataFrame, table_name : str):
        '''
        Uploads dataframe to AWS RDS, replaces table if exists
        Args:
            data_frame: dataframe to be uploaded 
            table_name: RDS table name 
        '''
        engine = self.__connect_database()
        data_frame.to_sql(table_name, engine, if_exists='replace')
        print('Uploading perfumes to RDS database...')
        
    def __update_table_rds(self, data_frame : pd.DataFrame, table_name : str):
        '''
        Uploads dataframe to AWS RDS, appends to table if exists
        Args:
            data_frame: dataframe to be uploaded 
            table_name: RDS table name 
        '''
        engine = self.__connect_database()
        data_frame.to_sql(table_name, con = engine, if_exists = 'append')
        print('Adding new perfumes to RDS database...')

    def __inspect_rds(self, table_name : str) -> pd.DataFrame:
        '''
        Reads RDS data as a dataframe 
        Args: 
            table_name: table to be inspected
        Returns: dataframe of all data on RDS table
        '''
        engine = self.__connect_database()
        table_data = pd.read_sql_table(table_name, engine)
        return table_data

    def __rds_columntolist(self, table : str, column : str) -> list:
        '''
        Converts data in a specified RDS table column to a list 
        Args:
            table: table to be insected
            column: name of column to be inspected
        Returns: a list containing all column data
        '''
        rds_df = self.__inspect_rds(table_name=table)
        list = rds_df[column].tolist()
        return list 

    def __rds_check_complete(self) -> list:
        '''
        Checks the RDS table for any rows with missing data and returns a list of product urls
        Args:
            table: RDS table to search
        Returns
            empty_urls: urls that have no corresponding data
        '''
        href_df = self.__sql_rds(sql_query='''SELECT href, price FROM "PerfumeScraper";''')
        empty_df = href_df[href_df.price == 'None'] 
        empty_values = empty_df.href.tolist()
        empty_urls = []
        for href in empty_values:
            url = self.__bloom_href(href=href)
            empty_urls.append(url)
        return empty_urls

    def __find_rdsunscraped(self, scraped_href : list, rds_href : list) -> list:
        '''
        Takes in a list of scraped hrefs and compares to the hrefs stored on RDS
        Args:
            scraped_href: list of new product hrefs scraped 
            rds_href: list of hrefs stored on RDS database
        Returns: a list of urls of products that do not have results on RDS
        '''
        rds_unscraped_url = []
        rds_unscraped_href = []
        for x in scraped_href:
            if x not in rds_href:
                url = self.__bloom_href(x)
                rds_unscraped_url.append(url)
                rds_unscraped_href.append(x)
        print('RDS new entries:', len(rds_unscraped_url))
        return rds_unscraped_url

    def __key_exists(self, mykey : str, mybucket : str):
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

    def __check_S3(self, href_list : list, s3_bucket : str) -> list:
        '''
        Takes in list of hrefs, checks whether their corresponding images exist in S3 bucket
        Args:
            href_list: list of product hrefs to  be checked against images on S3 bucket
        Returns: list of urls of products without images on S3
        '''
        s3_noimg = []
        for href in href_list:
            mykey = str(href) + '.jpg'
            result = self.__key_exists(mykey, s3_bucket)
            if result == False:
                url = self.__bloom_href(href)
                s3_noimg.append(url)
            else:
                pass
        print("Not on s3: ", len(s3_noimg))
        return s3_noimg

    def __sql_rds(self, sql_query : str) -> pd.DataFrame:
        '''
        Takes in sql query as string
        Args: 
            sql_query: sql query in string form 
        Returns pandas dataframe
        '''
        engine = self.__connect_database() 
        result = pd.read_sql(sql=sql_query, con=engine)
        return result

    def __href_to_url(self, base_url : str, href : str) -> str:
        '''
        Creates full url from base_url and href
        '''
        return base_url + href

    def __url_to_href(self, url : str) -> str:
        '''
        Converts full url to product href (unique identifier)
        '''
        split = url.split("s/")
        return split[1]

    def __url_href_list(self, urls : str) -> list:
        '''
        Takes list of urls
        Returns list of hrefs 
        '''
        scraped_href_list = []
        for x in urls:
            href = self.__url_to_href(x)
            scraped_href_list.append(href)
        return scraped_href_list

    def __bloom_href(self, href : str) -> str:
        '''
        Creates full url from product href
        '''
        return self.__href_to_url(base_url='https://bloomperfume.co.uk/products/', href=href)

    def __get_urls(self, main_url : str) -> list:
        '''
        Scrapes product urls from main product page url
        Args: main_url: main product page url
        Returns: list of urls 
        '''
        self._open_webpage(main_url)
        try:
            container = self.driver.find_element(By.XPATH, '//div[@class="products-list"]')
            prod_list = container.find_elements(By.CLASS_NAME, "product-name")
            url_list = self._loop_elements(prod_list, self._get_attr, 'href')
        except NoSuchElementException:
            url_list = ['None', 'None']
            print('Could not find urls')
        return url_list

    def __multiple_urls(self, no_pages : int) -> list:
        '''
        Scrapes multiple pages for urls
        Args:
            no_pages: number of pages of product to loop through
        Returns: a list of product urls
        '''
        all_links = []
        for i in range(1, (no_pages+1), 1):
            paged_url = self.url + "?page=" + str(i)
            list_i = self.__get_urls(paged_url)
            all_links += list_i
        return all_links

    def __loop_scrape(self, url_list : list) -> list:
        '''
        Takes in a list of urls and scrapes each page
        Args: 
            url_list: list of product urls to be scraped
        Returns: list of individual dictionaries
        '''
        dict_list = []
        for url in url_list:
            self._open_webpage(url)
            result = self._scrape_page(self.format)
            result['href'] = self.__url_to_href(url)
            result['url'] = url
            dict_list.append(result)
            # result['image_link'] = self.get_xpathattr('/html/body/div[4]/main/div[2]/div/div[2]/div/div[2]/div/div/img', 'src')
        return dict_list

    def __connect_database(self):
        creds = self.path + '/data_collection_pipeline/Data_Collection_Pipeline/creds/rds_creds.yaml'
        with open(creds, 'r') as f:
            creds = yaml.safe_load(f)
        DATABASE_TYPE= creds['DATABASE_TYPE']
        DBAPI= creds['DBAPI']
        USER= creds['USER']
        PASSWORD= creds['PASSWORD']
        ENDPOINT= creds['ENDPOINT']
        PORT= creds['PORT']
        DATABASE= creds['DATABASE']
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        engine.connect()
        return engine

    def run_scraper_RDS(self, no_pages : int):
        '''
        This method scrapes the number of pages supplied for new products, compares against data stored on RDS and also checks for incomplete entries on RDS.
        The data is then scraped and RDS table updated
        Args:
            no_pages: number of product pages to scrape (up to 42)
        Returns:
            updated table on RDS database 
        '''
        self.__connect_database()
        new_urls = self.__multiple_urls(no_pages)
        new_hrefs = self.__url_href_list(new_urls)
        # inspects the cloud database and produces a list of hrefs stored
        rds_hrefs = self.__rds_columntolist(table=self.table, column='href')
        url_list = self.__find_rdsunscraped(new_hrefs, rds_hrefs)
        # checks rds for incomplete entries
        url_list_2 = self.__rds_check_complete()
        url_list.append(url_list_2)
        new_data = self.__loop_scrape(url_list)
        new_dict = self._list_to_dict(new_data)
        new_df = self._dict_to_pd(new_dict)
        self.__update_table_rds(new_df, self.table)

    def run_scraper_local(self, no_pages : int): 
        '''
        Compares product data stored locally to newly scraped urls. 
        Only scrapes from products not present in the local json file. 
        Creates dictionary if it does not exist already.
        Args:
            no_pages: number of product pages to be scraped
        Returns:
            json file with scraped items
        '''
        new_urls = self.__multiple_urls(no_pages)
        new_hrefs = self.__url_href_list(new_urls)
        data_directory = self.path + '/data_collection_pipeline/data/'
        local_data = data_directory + 'Sample_dict_v2.json'
        if os.path.exists(local_data) == True:
            stored_dict = self._open_json(local_data)
            href_list = stored_dict['href']
            url_notindict = []
            for href in new_hrefs:
                if href not in href_list:
                    url = self.__bloom_href(href)
                    url_notindict.append(url)
            new_data_list = self.__loop_scrape(url_notindict)
            updated = [local_data, new_data_list]
            new_dict = self._list_to_dict(updated)

        else:
            print(new_urls)
            # new_url = [new_urls[0], new_urls[1]]
            result = self.__loop_scrape(new_urls)
            print(len(result))
            new_dict = self._list_to_dict(result)
            self._close_webpage()
        # self._dump_json(local_data, new_dict, 'Sample_dict_v2.json')
        # print("Storing data locally...")


example_list = ['https://bloomperfume.co.uk/products/canvas', 'https://bloomperfume.co.uk/products/figuier-noir', 'https://bloomperfume.co.uk/products/pg20-1-sorong']
example_listfdicts= [{'name': 'Canvas', 'price': '£110.00', 'concentration': '£110.00, 50 ml EdP', 'brand': 'Der Duft', 'description': ['', '']}, {'name': 'Figuier Noir', 'price': '£135.00', 'concentration': '£135.00, 100 ml EdP', 'brand': 'Houbigant', 'description': ['', '', '', '']}, {'name': 'PG20.1 Sorong', 'price': '£138.00', 'concentration': '£138.00, 100 ml EdP', 'brand': 'Pierre Guillaume - Parfumerie Générale', 'description': ['']}]

if __name__ == '__main__':
    myscraper = PerfumeScraper(bucket='imagebucketaic', table='PerfumeScraper')
    result = myscraper.run_scraper_local(no_pages=1)
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


    