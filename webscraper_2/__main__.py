import argparse
from webscraper_2.scraper_v2 import PerfumeScraper

print("Welcome to the Perfume Scraper")

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--option", type=str, required=True, help="choose either cloud or local")
parser.add_argument("-n", "--number", type=int, required=True, help="specify the number of pages to be scraped, min 2 max 45")
args = parser.parse_args()
number = args.number
option = args.option

myscraper = PerfumeScraper(bucket='aicpinterest/images', table='PerfumeScraper')

if option == 'local':
    myscraper.run_scraper_local(no_pages=number)
elif option == 'cloud':
    myscraper.run_scraper_RDS(no_pages=number)
else:
    print("Error, please try again")

myscraper.close_webpage()