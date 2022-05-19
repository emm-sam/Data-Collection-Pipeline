from selenium import webdriver
import time
from time import sleep
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import uuid

class PerfumeScraper: 
   

   # FOR WEBSITE NAVIGATION
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

if __name__ == '__main__':      
    my_scraper = PerfumeScraper("https://bloomperfume.co.uk/collections/perfumes")