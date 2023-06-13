# demo.py
from scrapeghost import SchemaScraper, CSS

scraper = SchemaScraper(
    {"date": "", "event_name": ""},
    # extra_preprocessors=[
    # ]
)
url = "https://mediapartychicago2023.sched.com/"
scraper.scrape(url)