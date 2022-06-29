# Data-Collection-Pipeline

Task: create methods to navigate a webpage

Task: bypass cookies 

Task: create method to get product page urls 

Task: retrive text and image data from product page 

Task: store data in dictionary 

Task: save dictionary locally 

Task: create method to find image link and download images locally 

Task: create unit tests for each public method 

Task: upload raw data folder to AWS S3

Task: upload tabular data to AWS RDS

Task: prevent rescraping of data (locally)

Task: prevent duplicate images being collected 

Task: prevent rescraping from remote database of tabular data 

create requirements.txt file

Task: create a Docker image which runs the scraper 

'''
from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage') 
    self.driver = webdriver.Chrome(options=chrome_options)

'''

?Add link to the dockerfile 
inside the dockerfile: 
    use python 
    download the latest version of chrome and chrome driver 
    intall the software in the requirements.txt folder 
    then run the webscraper package

## Task: Run docker in an EC2 instance 

- create EC2 instance 
- 'sudo yum update' was prompted 
- download docker within EC2 instance https://www.cyberciti.biz/faq/how-to-install-docker-on-amazon-linux-2/ using these instructions 
- aws configure within 

terminal commands: 
to create the docker image (be inside the directory with DOCKERFILE)
    docker build -t nameimage:tag .
to create/run the container:
    docker run --name containername -dit imagename
-it runs the file in interactable mode
-d runs in detached mode (for use on EC2)
start with 'sudo' when on EC2 (amazon linux 2)

fixes: 
- needed to change the security input option for RDS database from my IP to any IP4

## Task: Set up a prometheus container to monitor your scraper
## Task: Monitor the docker container 
## Task: Monitor the EC2 instance hardware metrics 
## Task: Observe these metrics and create a Grafana dashboard
## Task: Set up a CI/CD pipeline: github workflow 
## Task: Automate the scraper with cronjobs and multiplexing
- connect to EC2 instance
- $ crontab -e # to edit cronjobs 

