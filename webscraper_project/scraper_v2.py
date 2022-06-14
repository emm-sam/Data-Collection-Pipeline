import json
from webbrowser import Chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from time import sleep
import uuid 
import os


class GenericScraper:
    def __init__(self, url):
        self.driver = webdriver.Chrome("/Users/emmasamouelle/Desktop/Scratch/data_collection_pipeline/chromedriver")
        self.url = url
        self.dict = {"href":['test', 'test'], "complete":['test', 'test'], "uuid":['test', 'test'], "name":['test', 'test'], "id":['123', '123'], "price":['£135', '£135'], "strength":['75ml / EdP', '75ml / EdP'], "category":['test', 'test'], "brand":['test', 'test'], "flavours":[['test', 'test'],['test', 'test']], "top notes":[['test', 'test'],['test', 'test']], "heart notes":[['test', 'test'],['test', 'test']], "base notes":[['test', 'test'],['test', 'test']], "image link":['test', 'test']}

    def open_webpage(self, url):
        self.driver.get(url)
        time.sleep(2)
        try:
            cookies_button = self.driver.find_element(By.CLASS_NAME, "accept")
            cookies_button.click()
        except NoSuchElementException:
            pass

    # TAKE IN WEBELEMENT
    def get_text(self, element): #5 #USED
        '''
        takes in webelement
        returns the text 
        '''
        var = element.text
        return var

    def get_attr(self,element, attribute:str): #3 #USED
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

    # def tupletodict(self, tuple:tuple):
    #     dct = dict((x, y) for x, y in tuple)
    #     return dct 


class PerfumeScraper(GenericScraper):
    def __init__(self):
        super().__init__("https://bloomperfume.co.uk/collections/perfumes")
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

    def loop_scrape(self, url_list:list):
        new_list = []
        for url in url_list:
            self.open_webpage(url)
            result = self.scrape_page(tup_list = self.format)
            new_list.append(result)
        return new_list

example_list = ['https://bloomperfume.co.uk/products/canvas', 'https://bloomperfume.co.uk/products/figuier-noir', 'https://bloomperfume.co.uk/products/pg20-1-sorong']


if __name__ == '__main__':
    myscraper = PerfumeScraper()
    print(myscraper.loop_scrape(example_list)) # list containing dictionary 
    