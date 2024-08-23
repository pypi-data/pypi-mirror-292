import json
import time
from typing import Optional
import requests
from bs4 import BeautifulSoup
from .models import GetScrapingParams, RetryConfig

RETRY_DELAY_MS = 200

class GetScrapingClient:
    """
    Use the GetScrapingClient to make requests to GetScraping.com's API.
    Usage:
    client = GetScrapingClient('YOUR_API_KEY')
    result = client.scrape(GetScrapingParams(
        url='https://example.com',
        method='GET',
        js_rendering_options=JavascriptRenderingOptions(
            wait_for_request='.*api\.example\.com.*data'
        )
    ))
    # Load the html with BeautifulSoup
    soup = BeautifulSoup(result.text, 'html.parser')
    # Fetch the headers returned from the scraped url
    headers = result.headers
    # Grab the returned cookies and use them in subsequent requests
    cookies = result.headers.get('set-cookie')
    result_with_cookies = client.scrape(GetScrapingParams(
        url='https://example.com/some_path',
        method='GET',
        cookies=cookies
    ))
    """

    def __init__(self, api_key: str):
        """
        Initialize the GetScrapingClient.

        :param api_key: The API key for your GetScraping subscription.
                        You can find this at https://getscraping.com/dashboard
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.api_url = 'https://api.getscraping.io'
        self.api_key = api_key

    def _request(self, url: str, params: GetScrapingParams) -> requests.Response:
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Accept-Encoding': '*',
        }
        data = params.model_dump(exclude_none=True)  # Use model_dump instead of dict

        if params.retry_config:
            return self._fetch_retry(url, params.retry_config, headers, data)
        return requests.post(url, headers=headers, json=data)

    def scrape(self, params: GetScrapingParams) -> requests.Response:
        """
        Perform a scraping request.

        :param params: GetScrapingParams object containing the request parameters
        :return: requests.Response object
        """
        if params.js_rendering_options and params.js_rendering_options.render_js:
            return self._request(f"{self.api_url}/scrape_with_js", params)
        return self._request(f"{self.api_url}/scrape", params)

    def _fetch_retry(self, url: str, retry_config: RetryConfig, headers: dict, data: dict) -> requests.Response:
        num_retries = max(retry_config.num_retries, 1)
        for attempt in range(num_retries):
            try:
                res = requests.post(url, headers=headers, json=data)
                
                success = True
                if retry_config.success_status_codes and res.status_code not in retry_config.success_status_codes:
                    success = False
                elif not 200 <= res.status_code < 400:
                    success = False
                if retry_config.success_selector:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    if not soup.select(retry_config.success_selector):
                        success = False
                
                if success or attempt == num_retries - 1:
                    return res
                
            except requests.RequestException as e:
                if attempt == num_retries - 1:
                    raise e

            time.sleep(RETRY_DELAY_MS / 1000)

        raise Exception("The request was unsuccessful after all retry attempts.")