# Data-Collection-Pipeline

This project was undertaken as part of the AiCore career accelerator program. The aim of the project was to create an industry-grade automated data collection pipeline collecting information from a website of my choice.

This project really developed my understanding of object oriented programming and principles of software design. There were many challenging aspects, especially using docker, but the results were very satisfying. I also created a second scraper in the webscraper_2 folder, to experiment with different ways of structuring the webscraping and data manipulation, in order to make the scraper more generic to use on other websites. I also wanted to try out inheritence in OOP. There are strengths and weaknesses to both, but I learnt a lot from the process. 

### Technologies used: 
- Python
- Selenium WebDriver 
- Unittest (unit testing framework)
- Sqlalchemy (Python SQL toolkit and Object Relational Mapper)
- Psycopg2 (Python PostgreSQL database adaptor)
- Boto3 (Python API for AWS services)
- Amazon Web Services (AWS)
    - Amazon Elastic Compute Cloud (EC2) -  virtual server
    - Amazon Relational Database Service (RDS) - cloud database
    - Amazon Simple Storage Service (S3) - data lake
- Docker (open platform for developing, shipping, and running applications)
- Prometheus (event monitoring and alerting)
- Grafana (analytics and interactive visualization)

### Main steps: 
- build a web scraper (stores text and image data locally and on the cloud)
- build a testing suite for scraper 
- build a docker image to run the scraper remotely 
- run the docker container on an EC2 instance
- monitor the EC2 and docker metrics with Prometheus
- visualise these metrics on Grafana
- create a CI/CD pipeline using github workflows, cronjobs, tmux 

### WEBSCRAPER OVERVIEW
See scraper.py in webscraper_project folder 
**PerfumeScraper class** contains all the methods needed to run the scraper.

There are 3 arguments to control how much data is collected and where it is stored (cloud database, cloud datalake, local directory). 

Main tasks overview:
- overcome accept cookies button
- navigate a webpage
- scraping data from a webpage (text and image)
- data conversion (between lists, dictionaries, json files, dataframes)
- data cleaning (pandas)
- downloading files
- interacting with local files 
- interracting with AWS RDS and S3
- preventing duplicate scraping

----------------------------------------

**Python learnings:**
classes and methods (object oriented programing)
for loops
data conversion 
secret yaml files
uuid codes 
docstrings
error handling
using os
pandas
docstrings
inheritance

------------------------

## Creating a Docker image which runs the scraper
Why?
- so the package can be used by any operating system and therefore be deployed remotely
- ease of scaling up  

The following chrome options are needed for selenium to run in a docker container: 
>https://stackoverflow.com/questions/45323271/how-to-run-selenium-with-chrome-in-docker

```

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage') 
self.driver = webdriver.Chrome(options=chrome_options)

```

Link to dockerfile: 
> ### Dockerfile: (https://github.com/emm-sam/Data-Collection-Pipeline/blob/main/Dockerfile)

Explanation of the dockerfile:

**FROM** - uses a base of python 3.8

**RUN** - downloads the latest version of chrome and chrome driver to docker image

**COPY** - copies all documents from the project root directory to the docker image (except those in docker ignore file)

**RUN** - intalls the software in the requirements.txt file

**EXPOSE** - port 5432 inside container 

**CMD** - runs the scraper package in the webscraper_project folder using python3


## Run the docker container on an EC2 instance 
Steps:
- create EC2 instance 
- download docker within EC2 instance https://www.cyberciti.biz/faq/how-to-install-docker-on-amazon-linux-2/ using these instructions 
- $ aws configure 
- change the security input option for RDS database from my IP to any IP4

	**terminal commands:**
	> $ docker login 

	to create the docker image (from the directory contaning the DOCKERFILE)
	> $ docker build -t nameimage:tag .
	 
	> $ docker push username/image:tag 

	once image created and pushed to dockerhub:
	> $ docker pull emmsam/scraper:latest 

	to create/run the container:

	> $ docker run --name containername -dit imagename 

	**-it** runs the file in interactable mode

	**-d** runs in detached mode (for use on EC2)
		
- I set up the container to interact with the cloud data lake and database, however data files can also be transferred from a docker container to localhost if needed 

## Set up a prometheus container to monitor your scraper
Steps:
- create a prometheus.yml file in the root of EC2   **$ sudo nano /root/prometheus.yml** 
- configure the targets as the EC2 instance public IP4 address: port
- port 9090 for prometheus, port 9100 for node exporter, port 9323 for docker
- change security groups on the EC2 instance to accept these ports
- localhost works the same as EC2 IP4 for prometheus
- the docker metrics address can be found in the file **/etc/docker/daemon.json**
- prometheus was run using a docker container with the following terminal command:

```
$ docker run --rm -d -p 9090:9090 --name prometheus -v /root/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus --config.file=/etc/prometheus/prometheus.yml --web.enable-lifecycle
```

 ### prometheus.yml:
<img width="450" alt="Screenshot 2022-06-29 at 20 31 31" src="https://user-images.githubusercontent.com/100299675/176520636-3b7bdf26-6451-499c-baf9-ab3419146b23.png">

- To update the prometheus docker container if prometheus.yml is altered 
> $ curl -X POST http://localhost:9090/-/reload 

### to access prometheus metrics:
- Type [EC2publicIP4]:9090/metrics into the address bar
- Prometheus targets working:
<img width="500" alt="Screenshot 2022-06-29 at 20 07 54" src="https://user-images.githubusercontent.com/100299675/176517200-0ddc9ffa-197a-4ae4-a3f9-6582a9e93220.png">

## Monitor the EC2 instance hardware metrics 
- Use node exporter
- download the latest version and run **$./node_exporter** (only works while running)
> (https://prometheus.io/docs/guides/node-exporter/) 


## Observe these metrics and create a Grafana dashboard
Install grafana, start grafana on local computer. Access localhost:3000 and change password.

### Example of prometheus metrics: 
<img width="500" alt="Screenshot 2022-06-30 at 20 05 12" src="https://user-images.githubusercontent.com/100299675/176760015-973b9f61-5dbc-4bac-a83c-337199a89774.png"> 

### Example of prometheus metrics on grafana dashboard:
<img width="500" alt="Screenshot 2022-06-30 at 20 20 38" src="https://user-images.githubusercontent.com/100299675/176760482-b3f2366c-c5b7-45f5-bc9a-2767b5983f92.png">

### Monitoring the docker containers:
Scraper was started at 19:52. Prometheus is the other docker container.
<img width="500" alt="Screenshot 2022-06-30 at 20 20 33" src="https://user-images.githubusercontent.com/100299675/176760397-f73d5332-28e2-4933-bfc6-75503055abc0.png">

### Monitoring the metrics of the EC2 instance:
Node exporter was exited at 19:52.

<img width="500" alt="Screenshot 2022-06-30 at 20 03 50" src="https://user-images.githubusercontent.com/100299675/176760194-cf556d03-0239-49d5-8dae-777e2ce7004f.png">
<img width="500" alt="Screenshot 2022-06-30 at 20 01 01" src="https://user-images.githubusercontent.com/100299675/176760685-45cd6b98-9394-4553-82cd-9b55ecc4b944.png">
<img width="500" alt="Screenshot 2022-06-30 at 20 00 55" src="https://user-images.githubusercontent.com/100299675/176760769-c0b85e53-ccfb-4bcf-98c9-f2da3b1f7890.png">



## Set up a CI/CD pipeline: github workflow 
Set up so that a git push on the main branch automatically creates a new docker image with the same name as previous
- The new image needs to be pulled from docker into the workspace 

See workflow: (https://github.com/emm-sam/Data-Collection-Pipeline/blob/main/.github/workflows/main.yml)

## Automate the scraper with cronjobs and multiplexing
To automate the scraper the interactable element had to be removed (AWS RDS authentication)
#### Options:
    - pass a yaml or json file to the docker container when run using **-v** flag 
    - Set environment variables to pass to the docker container: 
        - Create a docker-compose.yml file and use **$ docker-compose up**
        - Create an **.env** file and pass to docker container using **--env-file** and **[pathto.envfile]**
            - Format is [VAR]=[VAL] e.g. **DATABASE_TYPE=postgresql**
#### Useful articles:
> - (https://rotempinchevskiboguslavsky.medium.com/environment-variables-in-container-vs-docker-compose-file-2426b2ec7d8b)
> - (https://docs.docker.com/compose/environment-variables/)

#### To run the docker container
```
 $ docker run --name new_scraper --env-file /home/ec2-user/.env emmsam/scraper:latest
```
#### Extra steps:
- **EXPOSE 5432** (in dockerfile - port)
- ensure RDS database security input allows access from EC2

#### Edit cronjobs on EC2 instance with **$ crontab -e**
<img width="680" alt="Screenshot 2022-06-29 at 17 41 23" src="https://user-images.githubusercontent.com/100299675/176490853-faf1559c-2c86-4fa9-a18f-4c396e7f2c1a.png">
 
 - 0 0 * * * means every night at midnight
 - pulls latest image, runs container, stops container, removes container 

#### Using tmux as a multiplexor
The EC2 instance will continue to run to allow the scraper to restart automatically 
> $ tmux 
- ensure logged in to docker on EC2
- manually exit the terminal, the EC2 instance will continue
- to reconnect use $tmux a
<img width="1020" alt="Screenshot 2022-06-29 at 17 45 23" src="https://user-images.githubusercontent.com/100299675/176491436-80791d28-1e07-4c85-9fef-929e686a4616.png">
