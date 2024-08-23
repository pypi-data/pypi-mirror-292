from typing import List, Dict, Union, Optional, Literal
from pydantic import BaseModel, Field

class InterceptRequestParams(BaseModel):
    intercepted_url_regex: str = Field(..., description="The regex matching the url to be intercepted")
    intercepted_url_method: str = Field("GET", description="The method of the request to intercept")
    request_number: int = Field(1, description="The request number to return if multiple matches")
    return_json: bool = Field(False, description="True if the response should be parsed and returned as JSON")

class RetryConfig(BaseModel):
    num_retries: int = Field(..., description="How many times to retry unsuccessful requests")
    success_status_codes: Optional[List[int]] = Field(None, description="The status codes that will render the request successful")
    success_selector: Optional[str] = Field(None, description="A css selector that needs to be present for a request to be considered successful")

class ProgrammableBrowserAction(BaseModel):
    type: str = Field(..., description="The type of action to perform")
    selector: Optional[str] = Field(None, description="The selector that triggers the action")
    javascript: Optional[str] = Field(None, description="The javascript to execute")
    wait_millis: Optional[int] = Field(None, description="The amount of time to wait for the action to complete")

class ProgrammableBrowserOptions(BaseModel):
    actions: List[ProgrammableBrowserAction] = Field(..., description="The actions to perform on the page")

class JavascriptRenderingOptions(BaseModel):
    render_js: bool = Field(False, description="Whether to render javascript or not")
    wait_millis: Optional[int] = Field(None, description="The time in milliseconds to wait before returning the result")
    wait_for_request: Optional[str] = Field(None, description="The URL (or regex matching the URL) that needs to be requested on page load")
    wait_for_selector: Optional[str] = Field(None, description="CSS or XPATH selector that needs to be present before returning the response")
    intercept_request: Optional[InterceptRequestParams] = Field(None, description="Configuration for intercepting a specific request")
    programmable_browser: Optional[ProgrammableBrowserOptions] = Field(None, description="Configuration for the programmable browser")

class GetScrapingParams(BaseModel):
    url: str = Field(..., description="The url to scrape - should include http:// or https://")
    method: Literal["GET", "POST", "PUT"] = Field(..., description="The method to use when requesting this url")
    response_type: Literal["text", "json", "buffer"] = Field("text", description="The expected response type")
    body: Optional[str] = Field(None, description="The payload to include in a post request")
    js_rendering_options: Optional[JavascriptRenderingOptions] = Field(None, description="Options for JavaScript rendering")
    cookies: Optional[List[str]] = Field(None, description="Define any cookies you need included in your request")
    headers: Optional[Dict[str, str]] = Field(None, description="The headers to attach to the scrape request")
    omit_default_headers: bool = Field(False, description="Omit default headers if set to true")
    use_isp_proxy: Optional[bool] = Field(None, description="Set to true to route requests through ISP proxies")
    use_residential_proxy: Optional[bool] = Field(None, description="Set to true to route requests through residential proxies")
    use_mobile_proxy: Optional[bool] = Field(None, description="Set to true to route requests through mobile proxies")
    use_own_proxy: Optional[str] = Field(None, description="URL of your own proxy server for this request")
    retry_config: Optional[RetryConfig] = Field(None, description="Configuration for when and how to retry a request")
    timeout_millis: int = Field(30000, description="How long to wait for the request to complete in milliseconds")