import logging
import os
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def save_html(content, file_path):
    try:
        # Save the HTML content to a file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logging.info(f'Documentation saved to {file_path}.')
    except OSError as e:
        logging.error(f'Error creating directory or writing file: {str(e)}')

def fetch_confluence_page(confluence, page_id):
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,version')
        return page
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

def crawl_confluence(confluence, page_id, base_directory, last_modified_date=None):
    title = get_page_title(confluence, page_id)
    sanitized_title = sanitize_filename(title)
    
    # Create directory structure based on page title
    child_pages = confluence.get_child_pages(page_id)
    if child_pages:
        directory = os.path.join(base_directory, sanitized_title)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    else:
        directory = base_directory
    
    page = fetch_confluence_page(confluence, page_id)
    if page:
        content = page['body']['storage']['value']
        modified_date = datetime.strptime(page['version']['when'], '%Y-%m-%dT%H:%M:%S.%f%z').date()
        
        if last_modified_date is None or modified_date > last_modified_date:
            file_path = os.path.join(directory, f"{sanitized_title}.html")
            save_html(content, file_path)
    
    # Recursively crawl child pages
    if child_pages:
        for child_page in child_pages:
            crawl_confluence(confluence, child_page['id'], directory, last_modified_date)