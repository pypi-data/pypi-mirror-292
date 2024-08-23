# GetScraping Python Client

This is the official Python client library for [GetScraping.com](https://getscraping.com), a powerful web scraping API service.

## Installation

You can install the GetScraping client library using pip:

```bash
pip install getscraping
```

## Usage

To use the GetScraping client, you'll need an API key from [GetScraping.com](https://getscraping.com). Once you have your API key, you can start using the client as follows:

```python
from getscraping import GetScrapingClient, GetScrapingParams

client = GetScrapingClient('YOUR_API_KEY')

def scrape_website():
    result = client.scrape(GetScrapingParams(
        url='https://example.com',
        method='GET'
    ))
    html = result.text
    print(html)

scrape_website()
```

## Features

The GetScraping client supports a wide range of features, including:

- Basic web scraping
- JavaScript rendering
- Custom headers and cookies
- Proxy support (ISP, residential, and mobile)
- Retrying requests
- Programmable browser actions
- Parameter validation using Pydantic models

## API Reference

### `GetScrapingClient`

The main class for interacting with the GetScraping API.

```python
client = GetScrapingClient(api_key: str)
```

### `scrape(params: GetScrapingParams)`

The primary method for scraping websites.

```python
result = client.scrape(params)
```

#### Scraping Parameters

The `GetScrapingParams` model supports the following options:

- `url` (str): The URL to scrape (should include http:// or https://)
- `method` (str): The HTTP method to use ('GET' or 'POST')
- `response_type` (str): The expected response type (default: "text")
- `body` (str, optional): The payload to include in a POST request
- `js_rendering_options` (JavascriptRenderingOptions, optional): Options for JavaScript rendering
- `cookies` (List[str], optional): List of cookies to include in the request
- `headers` (Dict[str, str], optional): Custom headers to attach to the request
- `omit_default_headers` (bool): If True, only use the headers you define (default: False)
- `use_isp_proxy` (bool, optional): Set to True to route requests through ISP proxies
- `use_residential_proxy` (bool, optional): Set to True to route requests through residential proxies
- `use_mobile_proxy` (bool, optional): Set to True to route requests through mobile proxies
- `use_own_proxy` (str, optional): URL of your own proxy server for this request
- `retry_config` (RetryConfig, optional): Configuration for when and how to retry a request
- `timeout_millis` (int): How long to wait for the request to complete in milliseconds (default: 30000)

JavaScript Rendering Options (`JavascriptRenderingOptions`):
- `render_js` (bool): Whether to render JavaScript or not
- `wait_millis` (int, optional): The time in milliseconds to wait before returning the result
- `wait_for_request` (str, optional): The URL (or regex matching the URL) that needs to be requested on page load
- `wait_for_selector` (str, optional): CSS or XPATH selector that needs to be present before returning the response
- `intercept_request` (InterceptRequestParams, optional): Configuration for intercepting a specific request
- `programmable_browser` (ProgrammableBrowserOptions, optional): Configuration for the programmable browser

Retry Configuration (`RetryConfig`):
- `num_retries` (int): How many times to retry unsuccessful requests
- `success_status_codes` (List[int], optional): The status codes that will render the request successful
- `success_selector` (str, optional): A CSS selector that needs to be present for a request to be considered successful

For more detailed information on these parameters, please refer to the [GetScraping documentation](https://docs.getscraping.com).

## Examples

### Basic Scraping
```python
from getscraping import GetScrapingClient, GetScrapingParams

client = GetScrapingClient('YOUR_API_KEY')

result = client.scrape(GetScrapingParams(
    url='https://example.com',
    method='GET'
))

html = result.text
print(html)
```

### Scraping with JavaScript Rendering
Render JavaScript to scrape dynamic sites.
Note: rendering JS will incur an additional cost (5 requests)
```python
from getscraping import GetScrapingClient, GetScrapingParams, JavascriptRenderingOptions

client = GetScrapingClient('YOUR_API_KEY')

result = client.scrape(GetScrapingParams(
    url='https://example.com',
    method='GET',
    js_rendering_options=JavascriptRenderingOptions(
        render_js=True,
        wait_millis=5000
    )
))

html = result.text
print(html)
```

### Using Various Proxies
Typically the best proxy type for bypassing tough anti-bot measures is mobile, then residential, then ISP, and lastly our default proxies. 

We recommend trying requests with the default to start and working your way up as necessary, as non-default proxies incur additional costs (costs are: 1 request for default proxies, 5 requests for ISP proxies, 25 for residential, and 50 for mobile).
```python
from getscraping import GetScrapingClient, GetScrapingParams

client = GetScrapingClient('YOUR_API_KEY')

result = client.scrape(GetScrapingParams(
    url='https://example.com',
    method='GET',
    use_residential_proxy=True
))

html = result.text
print(html)
```

### Retrying Requests
```python
from getscraping import GetScrapingClient, GetScrapingParams, RetryConfig

client = GetScrapingClient('YOUR_API_KEY')

result = client.scrape(GetScrapingParams(
    url='https://example.com',
    method='GET',
    retry_config=RetryConfig(
        num_retries=3,
        success_status_codes=[200]
    )
))

html = result.text
print(html)
```

### Using Programmable Browser Actions
```python
from getscraping import GetScrapingClient, GetScrapingParams, JavascriptRenderingOptions, ProgrammableBrowserOptions, ProgrammableBrowserAction

client = GetScrapingClient('YOUR_API_KEY')

result = client.scrape(GetScrapingParams(
    url='https://example.com',
    method='GET',
    js_rendering_options=JavascriptRenderingOptions(
        render_js=True,
        programmable_browser=ProgrammableBrowserOptions(
            actions=[
                ProgrammableBrowserAction(
                    type='click',
                    selector='#submit-button'
                ),
                ProgrammableBrowserAction(
                    type='wait',
                    wait_millis=2000
                )
            ]
        )
    )
))

html = result.text
print(html)
```

## Advanced Usage

For more advanced usage, including intercepting requests and other programmable browser actions, please refer to the [GetScraping documentation](https://docs.getscraping.com).

## Support

If you encounter any issues or have questions, please send us a message [support@getscraping.com](mailto:support@getscraping.com) or open an issue in the [GitHub repository](https://github.com/GetScraping/get-scraping-python/issues).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.