# Crawler Function HTTP

This project is a web crawler implemented using Azure Functions. It fetches HTML content from a given URL, parses it, and saves the content to a local directory structure. The crawler also follows links within the same domain and saves their content as well.

## Features

- Fetches and saves HTML content from a given URL.
- Parses the URL to create a directory structure for saving files.
- Follows links within the same domain and saves their content.
- Logs the progress and errors during the crawling process.

## Requirements

- Python 3.6 or higher
- Azure Functions Core Tools
- Requests library
- BeautifulSoup library

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/CrawlerFunctionHttp.git
    cd CrawlerFunctionHttp
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Deploy the function to Azure Functions or run it locally using Azure Functions Core Tools.

## Usage

1. Trigger the function by sending an HTTP request with the URL to crawl:
    ```sh
    curl -X POST "http://localhost:7071/api/CrawlerFunctionHttp" -d "url=https://example.com"
    ```

2. The crawled HTML content will be saved in the `collected_docs` directory.

## Logging

The function logs its progress and any errors encountered during the crawling process. Check the logs for detailed information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.