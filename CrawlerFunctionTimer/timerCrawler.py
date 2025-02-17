import logging
from datetime import datetime
from crawler_utils import sanitize_filename, save_html, fetch_confluence_page, get_page_title, crawl_confluence

# Configure logging
logging.basicConfig(level=logging.INFO)