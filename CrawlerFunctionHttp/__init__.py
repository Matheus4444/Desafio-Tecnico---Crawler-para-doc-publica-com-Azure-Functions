import logging
import azure.functions as func
from atlassian import Confluence
from .httpCrawler import crawl_confluence
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')

    try:
        space_key = req.params.get('space_key')
        confluence_url = req.params.get('confluence_url')
        last_modified_date_str = req.params.get('last_modified_date')
        
        if not space_key or not confluence_url:
            return func.HttpResponse("Please provide a space key and Confluence URL.", status_code=400)

        confluence = Confluence(
            url=confluence_url
        )

        last_modified_date = None
        if last_modified_date_str:
            last_modified_date = datetime.strptime(last_modified_date_str, '%Y-%m-%d').date()

        base_directory = 'collected_docs'
        root_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000, expand='body.storage')
        for root_page in root_pages:
            crawl_confluence(confluence, root_page['id'], base_directory, last_modified_date)

        return func.HttpResponse(f'Documentation successfully crawled and saved.', status_code=200)
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return func.HttpResponse(f'An error occurred: {str(e)}', status_code=500)