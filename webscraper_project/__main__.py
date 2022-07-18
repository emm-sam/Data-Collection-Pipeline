from .scraper import PerfumeScraper

print("Hello and welcome to bloom_scraper 1.0")
my_scraper = PerfumeScraper("https://bloomperfume.co.uk/collections/perfumes", container=False)
my_scraper.run_scraper(no_pages=1)
my_scraper.close_webpage()