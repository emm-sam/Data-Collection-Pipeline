import os
import requests
import time
import urllib.request
from sqlalchemy import func
import urllib3.exceptions
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webbrowser import Chrome

base_dir = os.getcwd()
path = base_dir + "/data_collection_pipeline/chromedriver"

class GenericScraper:
    def __init__(self):
        self.driver = webdriver.Chrome(path)

    def open_webpage(self, url : str):
        '''
        Opens webpage
        Args: url: url to be opened
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
        Closes current open browser
        '''
        self.driver.quit()

    def get_current_url(self) -> str:
        '''
        Returns current url
        '''
        return self.driver.current_url

    # TAKE IN WEBELEMENT
    def get_text(self, element : webdriver) -> str: #5 #USED
        '''
        Takes in webelement
        Returns the text 
        '''
        try:
            var = element.text
        except NoSuchElementException:
            var = None
        return var

    def get_attr(self, element : webdriver, attr : str) -> str: 
        '''
        Takes in webelement and attributename, returns attribute content
        Args: 
            element: webelement
            attr: name of attribute
        Returns: content of attribute as a string
        '''
        try:
            var = str(element.get_attribute(attr))
        except NoSuchElementException:
            var = None
        return var 

    def get_relxpathtext(self, element : webdriver, relxpath : str) -> str:
        '''
        Takes in webelement and relative xpath, returns text of that xpath
        Args: 
            element: webelement
            relxpath: relative xpath 
        Returns: text contained in relative xpath
        '''
        try:
            var = element.find_element(By.XPATH, relxpath).text
        except NoSuchElementException:
            var = None
        return var

    # TAKE IN XPATH
    def get_xpathtext(self, xpath : str) -> str:
        '''
        Args: xpath: xpath of text required
        Returns: text from that xpath
        '''
        try:
            var = self.driver.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            var = None
        return var

    def get_xpathattr(self, xpath : str, attr : str) -> str:
        '''
        Args: 
            xpath: xpath of required attribute
            attr: name of required attibute
        Returns: content of the attribute 
        '''
        try:
            area = self.driver.find_element(By.XPATH, xpath)
            var = area.get_attribute(attr)
        except NoSuchElementException:
            var = None
        return var

    def get_bin(self, bin_xpath : str, bin_tag : str) -> list:
        '''
        Args:
            bin_xpath: xpath to the container to be looped through
            bin_tag: tag of the individual sections to be looped through 
        Returns: list of webelements with that tag 
        '''
        try:
            bin = self.driver.find_element(By.XPATH, bin_xpath)
            variable_list = bin.find_elements(By.TAG_NAME, bin_tag)
        except NoSuchElementException:
            variable_list = [None, None]
        return variable_list 

    # COMBINE NAME AND METHOD 
    def make_tuple(self, name : str, func, arg : str) -> tuple:
        '''
        Tuple that contains the variable and the variable contents from the webpage
        Args:
            name: name of the variable being extracted
            func: funtion to use when scraping the page
            arg: argument for the funtion used 
        Returns: a tuple of the variable name and the content from the scraped variable
        '''
        var = func(arg)
        tuple = (name, var)
        return tuple

    def loop_elements(self, list : list, func, arg : str) -> list:
        '''
        Returns the content from the webelements supplied
        Args:
            list: list of webelements 
            func: function to apply to the webelements
            arg: argument for the supplied function 
        Returns: a list of scraped information
        '''
        new_list = []
        for l in list:
            if arg != 'no_arg':
                var = func(l, arg)
            else:
                var = func(l)
            new_list.append(var)
        return new_list

    def tuple_multiple(self, name : str, bin_xpath : str, bin_tag : str, func, arg : str) -> tuple:
        '''
        Scrapes webpage and creates a variable and content tuple for variables with more than one data point 
        Args:
            name: name of variable
            bin_xpath: xpath to the container to be looped through
            bin_tag: tag of the element containing the content to be looped through
            func: function to apply to retrieve the content  
            arg: argument for the function above
        Returns: tuple of variable name and list of content scraped from the webapage
        '''
        bin_tags = self.get_bin(bin_xpath=bin_xpath, bin_tag=bin_tag)
        new_list = self.loop_elements(bin_tags, func, arg)
        tuple = (name, new_list) 
        return tuple

    # DATA COLLECTION
    def scrape_page(self, tup_tup : tuple) -> tuple:
        '''
        Takes in a tuple of tuples of length 3 or 5 (must be in the required format)
        Args: tup_tup: format either 
            (variable name, function, argument) or
            (variable name, bin_xpath, bin_tag, function, argument)
        Returns: a dictionary with the variable name as key
        '''
        new_list = []
        for tup in tup_tup:
            if len(tup) == 3:
                scraped = self.make_tuple(tup[0], tup[1], tup[2])
                new_list.append(scraped)
            elif len(tup) == 5:
                scraped = self.tuple_multiple(tup[0], tup[1], tup[2], tup[3], tup[4])
                new_list.append(scraped)
            else:
                print('Error, check your input is valid')
        new_tuple = (*new_list,) # converts list to tuple 
        dct = dict((x, y) for x, y in new_tuple) # convert tuples to dict 
        return dct

    def download_image(self, image_link : str, file_name : str, dir_path : str):
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
