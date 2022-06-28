from webbrowser import Chrome
from selenium import webdriver
import time
from time import sleep
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
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
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import yaml

class PerfumeScraper: 
   
    def __init__(self, url:str): #creds: str='config/RDS_creds.yaml')
        # options = webdriver.ChromeOptions() 
        options = Options()
        # options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage') 
        options.add_argument('--remote-debugging-port=9222')
        self.driver = webdriver.Chrome(options=options)
        # self.driver = webdriver.Chrome("/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline/chromedriver")
        # self.driver = Chrome(ChromeDriverManager().install(), options=options)

        self.url = url
        self.dict = {"href":['test', 'test'], "complete":['test', 'test'], "uuid":['test', 'test'], "name":['test', 'test'], "id":['123', '123'], "price":['£135', '£135'], "strength":['75ml / EdP', '75ml / EdP'], "category":['test', 'test'], "brand":['test', 'test'], "flavours":[['test', 'test'],['test', 'test']], "top notes":[['test', 'test'],['test', 'test']], "heart notes":[['test', 'test'],['test', 'test']], "base notes":[['test', 'test'],['test', 'test']], "image link":['test', 'test']}
        self.s3 = boto3.client('s3')
        self.bucket = 'imagebucketaic'
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        DATABASE = 'postgres'
        ENDPOINT = input('RDS endpoint: ') 
        USER = input('User: ')
        PASSWORD = input('Password: ') 
        PORT = input('Port: ')

        # with open(creds, 'r') as f:
        #     creds = yaml.safe_load(f)
        # DATABASE_TYPE= creds['DATABASE_TYPE']
        # DBAPI= creds['DBAPI']
        # USER= creds['USER']
        # PASSWORD= creds['PASSWORD']
        # ENDPOINT= creds['ENDPOINT']
        # PORT= creds['PORT']
        # DATABASE= creds['DATABASE']
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        
    # FOR WEBSITE NAVIGATION

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

    def search_website(self, input:str):
        url = 'https://bloomperfume.co.uk/search?q=' + input
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

    # COLLECTING DATA FROM THE WEBSITE

    def get_links(self, url):
        self.open_webpage(url)
        time.sleep(1)
        try:
            product_container = self.driver.find_element(By.XPATH, '//div[@class="products-list"]')
            prod_list = product_container.find_elements(By.CLASS_NAME, "product-name")
            link_list = [] 
            for p in prod_list:
                href = p.get_attribute("href")
                link_list.append(href)
        except:
            pass
        return link_list

    def get_multiple_links(self, number_pages):
        all_links = []
        for i in range(1, (number_pages+1), 1):
            paged_url = self.url + "?page=" + str(i)
            list_i = self.get_links(paged_url)
            all_links += list_i
        return all_links

    def clean_list(self, list):
        cleaned_list = []
        for l in list:
            if l != None:
                cleaned_list.append(l)
        return cleaned_list

    def scrape_product(self, url):
        self.open_webpage(url)
        product_dictionary = {"href":[], "complete":[], "uuid":[], "name":[], "id":[], "price":[], "strength":[], "category":[], "brand":[], "flavours":[], "top notes":[], "heart notes":[], "base notes":[], "image link":[]}
        
        current_url = self.driver.current_url
        split = current_url.split("s/")
        product_dictionary['href']=split[1]
        product_dictionary['complete']='True'
        product_dictionary['uuid']=str(uuid.uuid4())
    
        try:
            main_details = self.driver.find_element(By.XPATH, '//*[@id="product-page"]/div/div[3]/div/div[1]/div[1]/div[1]/a')
            product_number = main_details.get_attribute("data-product") 
            product_dictionary['id']=product_number
            product_price = main_details.get_attribute("data-price")
            product_dictionary['price']=product_price
            product_title = main_details.get_attribute("data-title")
            product_dictionary['name']=product_title
            product_vtitle = main_details.get_attribute("data-vtitle")
            product_dictionary['strength']=product_vtitle
            product_category = main_details.get_attribute("data-cat")
            product_dictionary['category']=product_category
            product_brand = main_details.get_attribute("data-vendor")
            product_dictionary['brand'] = product_brand

            flavours = self.driver.find_element(By.XPATH, '//*[@id="product-page"]/div/div[1]/div/div[2]')
            flavs = flavours.find_elements(By.TAG_NAME, "div")
            perfume_flavours = []
            for f in flavs:
                flav = f.get_attribute("data-flavor")
                perfume_flavours.append(flav)
            product_dictionary['flavours']= perfume_flavours

            top_notes = self.driver.find_element(By.XPATH, '//*[@id="product-page"]/div/div[3]/div/div[6]/div[1]')
            t_notes = top_notes.find_elements(By.TAG_NAME, "span")
            top = []
            for t in t_notes:
                note = t.get_attribute("data-search")
                top.append(note)
            top = self.clean_list(top)
            product_dictionary['top notes']= top

            heart_notes = self.driver.find_element(By.XPATH, '//*[@id="product-page"]/div/div[3]/div/div[6]/div[2]')
            h_notes = heart_notes.find_elements(By.TAG_NAME, "span")
            heart = []
            for h in h_notes:
                note2 = h.get_attribute("data-search")
                heart.append(note2)
            heart = self.clean_list(heart)
            product_dictionary['heart notes'] = heart

            base_notes = self.driver.find_element(By.XPATH, '//*[@id="product-page"]/div/div[3]/div/div[6]/div[3]')
            b_notes = base_notes.find_elements(By.TAG_NAME, "span")
            base = []
            for b in b_notes:
                note3 = b.get_attribute("data-search")
                base.append(note3)
            base = self.clean_list(base)
            product_dictionary['base notes'] = base

            im_link = self.driver.find_element(By.XPATH, '//*[@id="product_pic_1"]')
            i_link = im_link.find_element(By.TAG_NAME, 'img')
            image_link = i_link.get_attribute('src')
            product_dictionary['image link']=image_link
            
        except NoSuchElementException: 
            product_dictionary['id'] = "None"
            product_dictionary['price'] = "None"
            product_dictionary['name'] = "None"
            product_dictionary['strength'] = "None"
            product_dictionary['category'] = "None"
            product_dictionary['brand'] = "None"
            product_dictionary['flavours'] = ["None"]
            product_dictionary['top notes'] = ["None"]
            product_dictionary['heart notes'] = ["None"]
            product_dictionary['base notes'] = ["None"]
            product_dictionary['image link'] = "None"
            product_dictionary['href'] = split[1] 
            product_dictionary['complete'] = 'False'
        return(product_dictionary)

    def scrape_add(self, list, original_dict):
        for url in list:
            perfume = self.scrape_product(url)
            original_dict["href"].append(perfume["href"])
            original_dict["complete"].append(perfume["complete"])
            original_dict["uuid"].append(perfume["uuid"])
            original_dict["name"].append(perfume["name"])
            original_dict["id"].append(perfume["id"])
            original_dict["price"].append(perfume["price"])
            original_dict["strength"].append(perfume["strength"])
            original_dict["category"].append(perfume["category"])
            original_dict["brand"].append(perfume["brand"])
            original_dict["flavours"].append(perfume["flavours"])
            original_dict["top notes"].append(perfume["top notes"])
            original_dict["heart notes"].append(perfume["heart notes"])
            original_dict["base notes"].append(perfume["base notes"])
            original_dict["image link"].append(perfume["image link"])
        return original_dict

    def make_test_dict(self):
        return self.dict

    def download_image(self, url, file_name, dir_path):
        self.driver.get(url) 
        time.sleep(1)
        try:
            im_link = self.driver.find_element(By.XPATH, '//*[@id="product_pic_1"]')
            i_link = im_link.find_element(By.TAG_NAME, 'img')
            image_link = i_link.get_attribute('src')
            self.driver.implicitly_wait(2)
            self.driver.get(image_link)
            full_path = dir_path + file_name + '.jpg'
            urllib.request.urlretrieve(image_link, full_path)
        except NoSuchElementException:
            pass

    def downloads_multiple_img(self, list, dir_path):
        for url in list:
            split = url.split("s/")
            href = split[1]
            full_path = dir_path + href +'.jpg'
            if os.path.exists(full_path) == False:
                self.download_image(url=url, file_name=href, dir_path=dir_path)
            else:
                pass

    # MANIPULATING AND STORING THE DATA 

    def dump_json(self, filepath, dict, dict_name):
        with open(os.path.join(filepath, dict_name), mode='w') as f:
            json.dump(dict, f)

    def data_clean(self, dictionary):
        def split_rename(df_column, new_name_stem):
            new_df = pd.DataFrame(df_column.tolist())
            column_list = new_df.columns

            def create_mapper(list, string):
                length = len(list)
                dict = {}
                for i in range(length):
                    no = str(i)
                    dictvalue = string + no
                    dict[i] = dictvalue
                return dict
            mapper = create_mapper(list=column_list, string=new_name_stem)
            renamed_df = new_df.rename(mapper=mapper, axis=1)
            return renamed_df

        df1 = pd.DataFrame.from_dict(dictionary, orient='index')
        df1 = df1.transpose()
    
        # data cleaning - strength and volume columns 
        df1['strength'] = df1['strength'].str.split('/')
        sub1 = pd.DataFrame(df1['strength'].tolist())
        sub1 = sub1.rename({0:'volume', 1:'strengths'}, axis=1)
        sub1['volume'] = sub1['volume'].str.replace('m','')
        sub1['volume'] = sub1['volume'].str.replace('l','')
        sub1['volume'] = sub1['volume'].str.replace(' ','')
        sub1['strengths'] = sub1['strengths'].str.replace('Extrait de Parfum', 'EdP')
        sub1['strengths'] = sub1['strengths'].str.replace('Parfum', 'Extrait')
        if sub1['volume'].empty:
            sub1['volume'] = sub1['volume'].astype(float)

        df2 = pd.concat([df1, sub1], axis=1)

        df2.drop(columns=['id'], inplace=True)
        df2.drop(columns=['category'], inplace=True)
        df2.drop(columns=['strength'], inplace=True)
        df2['price'] = df2['price'].str.replace('£','')
        if df2['price'].empty:
            df2['price'] = df2['price'].astype(float)   
    
        column_order = ['href', 'uuid', 'name', 'price', 'volume', 'strengths', 'brand', 'flavours', 'top notes',
       'heart notes', 'base notes', 'image link']
        df2 = df2.reindex(columns=column_order)

        subf = split_rename(df2['flavours'], 'F')
        subtn = split_rename(df2['top notes'], 'TN')
        subhn = split_rename(df2['heart notes'], 'HN')
        subbn = split_rename(df2['base notes'], 'BN')

        df3 = pd.concat([df2, subf, subtn, subhn, subbn], axis=1)
        # clean_dict = df3.to_dict()
        return df3

    def open_json(self, file_path):
        with open(file_path, mode='r') as f:
            data = json.load(f)
            return data

    def uploadDirectory(self, dir_path):
        bucket = self.bucket
        for (root, dirs, files) in os.walk(dir_path):
            for file in files:
                self.s3.upload_file(os.path.join(root,file),bucket,file)

    def update_databse_rds(self, data_frame, table_name):
        self.engine.connect()
        data_frame.to_sql(table_name, self.engine, if_exists='replace')

    def update_table_rds(self, data_frame, table_name):
        self.engine.connect()
        data_frame.to_sql(table_name, con = self.engine, if_exists = 'append')

    def inspect_rds(self, table):
        self.engine.connect()
        # table = 'PerfumeScraper'
        table_data = pd.read_sql_table('PerfumeScraper', self.engine)
        # pd.read_sql_query('''SELECT * FROM actor LIMIT 10''', engine)
        return table_data

    def key_exists(self, mykey, mybucket):
        # s3_client = boto3.client('s3')
        try:
            response = self.s3.list_objects_v2(Bucket=mybucket, Prefix=mykey)
            if response:
                for obj in response['Contents']:
                    if mykey == obj['Key']:
                        return True
        except:
            return False
            pass

    # INTEGRATING THE ABOVE

    def run_scraper(self, no_pages):
        # scrapes the urls of all the products 
        url_links = self.get_multiple_links(no_pages) #42 

        # creates a list of hrefs from the scraped urls (contains all possible hrefs)
        href_list = []
        for x in url_links:
            text = str(x)
            href = text.split("s/")
            href_list.append(href[1])
        
        # inspects the cloud database and produces a list of hrefs stored
        rds_df = self.inspect_rds(table = 'PerfumeScraper')
        rds_href_list = rds_df['href'].tolist()

        rds_unscraped_url = []
        rds_unscraped_href = []
        for x in href_list:
            if x not in rds_href_list:
                stem = 'https://bloomperfume.co.uk/products/'
                url = stem + str(x)
                rds_unscraped_url.append(url)
                rds_unscraped_href.append(x)

        print('rds unscraped:', len(rds_unscraped_href))

        # upload existing database (hardcopy)
        # existing_dict = self.open_json('/Users/emmasamouelle/Desktop/Scratch/Data_Pipeline/raw_data/Sample_Perfume_Dict.json')
        
        # scrape the new list and add to empty dictionary
        extra_dict = self.scrape_add(rds_unscraped_url, self.dict)
        # if extra_dict == True:
        #     if existing_dict == True:
        #         total_dict = self.add_dict(existing_dict, extra_dict)
        #         self.dump_json(filepath, total_dict, 'Sample_Perfume_Dict.json')
       
        # self.dump_json(filepath='/Users/emmasamouelle/Desktop/Scratch/old_pipeline', dict=extra_dict, dict_name='Sample_Perfume_Dict.json')
        # cleans the dictionary and turns into pd dataframe, appends to rds 
        clean_df = self.data_clean(extra_dict)
        self.update_table_rds(data_frame=clean_df, table_name='PerfumeScraper')

        # s3_noimg = []
        # for x in href_list:
        #     key = str(x) + '.jpg'
        #     result = self.key_exists(mykey=key, mybucket='imagebucketaic')
        #     if result == False:
        #         stem = 'https://bloomperfume.co.uk/products/'
        #         url = stem + str(x)
        #         s3_noimg.append(url)
        #     else:
        #         pass
        # print("not on s3: ", len(s3_noimg))
        # print(s3_noimg)

        # if len(s3_noimg) > 1:
        #     self.downloads_multiple_img(list=s3_noimg, dir_path=filepath)
        # elif len(s3_noimg) == 1:
        #     print('needs single download')
        #     print(s3_noimg)
        # else:
        #     pass

        # no_img = []
        # for x in rds_unscraped_href:
        #     full_path = filepath + str(x) + '.jpg'
        #     if os.path.exists(full_path) == False:
        #         # print(full_path)
        #         stem = 'https://bloomperfume.co.uk/products/'
        #         url = stem + str(x)
        #         no_img.append(url)
        #         # self.download_image(url=url, file_name=href, dir_path=filepath)
        # print("no_img:", len(no_img))

        # if len(no_img) > 1:
        #     self.downloads_multiple_img(list=no_img, dir_path=filepath)
        # elif len(no_img) == 1:
        #     print('needs single download')
        #     print(no_img)
        # else:
        #     pass
          
        # self.uploadDirectory(filepath)
        print("----------------------")
        

if __name__ == '__main__':      
    my_scraper = PerfumeScraper("https://bloomperfume.co.uk/collections/perfumes")
    my_scraper.open_webpage("https://bloomperfume.co.uk/collections/perfumes")
    my_scraper.run_scraper(no_pages=1)
    my_scraper.close_webpage()
