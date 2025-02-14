import logging
import azure.functions as func
from atlassian import Confluence
from .timerCrawler import crawl_confluence
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Timer trigger function executed at %s', mytimer.schedule_status['Last'])

    # URL of the Confluence instance
    confluence_url = "https://sapiensia.atlassian.net/"

    # Space key of the documentation to crawl
    space_key = "SIA"

    confluence = Confluence(
        url=confluence_url
    )

    # Calculate the date for the last day
    last_modified_date = datetime.utcnow().date() - timedelta(days=1)

    base_directory = 'collected_docs'
    root_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000, expand='body.storage')
    for root_page in root_pages:
        crawl_confluence(confluence, root_page['id'], base_directory, last_modified_date)

    logging.info('Documentation successfully crawled and saved.')