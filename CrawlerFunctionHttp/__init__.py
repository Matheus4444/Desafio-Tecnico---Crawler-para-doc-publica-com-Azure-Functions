import logging
import os
import azure.functions as func
import re
from atlassian import Confluence

# Configure logging
logging.basicConfig(level=logging.INFO)

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def save_html(content, directory, file_name):
    try:
        # Save the HTML content to a file
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
        logging.info(f'Documentation saved to {file_name}.')
    except OSError as e:
        logging.error(f'Error creating directory or writing file: {str(e)}')

def fetch_confluence_page(confluence, page_id):
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage')
        return page['body']['storage']['value']
    except Exception as e:
        logging.error(f'Error fetching page content for ID {page_id}: {str(e)}')
        return None

def get_page_title(confluence, page_id):
    try:
        page = confluence.get_page_by_id(page_id, expand='title')
        return page['title']
    except Exception as e:
        logging.error(f'Error fetching page title for ID {page_id}: {str(e)}')
        return 'index'

def crawl_confluence(confluence, page_id, base_directory):
    title = get_page_title(confluence, page_id)
    sanitized_title = sanitize_filename(title)
    
    # Create directory structure based on page title
    directory = os.path.join(base_directory, sanitized_title)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    file_name = os.path.join(directory, f"{sanitized_title}.html")
    
    content = fetch_confluence_page(confluence, page_id)
    if content:
        save_html(content, directory, file_name)
    
    # Recursively crawl child pages
    child_pages = confluence.get_child_pages(page_id)
    for child_page in child_pages:
        crawl_confluence(confluence, child_page['id'], directory)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')

    try:
        space_key = req.params.get('space_key')
        confluence_url = req.params.get('confluence_url')
        if not space_key or not confluence_url:
            return func.HttpResponse("Please provide a space key and Confluence URL.", status_code=400)

        confluence = Confluence(
            url=confluence_url
        )

        base_directory = 'collected_docs'
        root_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000, expand='body.storage')
        for root_page in root_pages:
            crawl_confluence(confluence, root_page['id'], base_directory)

        return func.HttpResponse(f'Documentation successfully crawled and saved.', status_code=200)
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return func.HttpResponse(f'An error occurred: {str(e)}', status_code=500)