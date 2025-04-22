import json
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OpenAIApiProxy:
    def __init__(self, api_key=None, api_base_url=None):
        """
        Initialize the API proxy with retry logic and session configuration.
        """
        # Retry strategy for handling failures
        retry_strategy = Retry(
            total=3,  # Maximum retry attempts (including initial request)
            backoff_factor=2,  # Time interval factor between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Status codes that should trigger a retry
        )
        
        # Adapter to use the retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        
        # Create a session and mount the adapter for both HTTP and HTTPS
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # API credentials
        self.api_key = api_key
        self.api_base_url = api_base_url

    def call(self, model_name, system_prompt, user_prompt, max_tokens=64, headers=None):
        """
        Makes a request to the API with the specified model, prompts, and token limits.
        Retries if an error occurs.
        """
        if headers is None:
            headers = {}

        attempt = 0
        max_backoff_time = 32  # Maximum wait time between retries (in seconds)

        while True:
            try:
                url = f"{self.api_base_url}/chat/completions"
                params = {
                    "model": model_name,
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "user", "content": user_prompt},
                    ]
                }

                headers['Content-Type'] = 'application/json'
                if self.api_key:
                    headers['Authorization'] = f"Bearer {self.api_key}"

                # Make the POST request
                response = self.session.post(url, headers=headers, data=json.dumps(params))

                # If successful, return the response as JSON
                if response.status_code == 200:
                    return response.json()

            except Exception as e:
                # Retry on failure
                attempt += 1
                wait_time = min(2 ** attempt, max_backoff_time)  # Exponential backoff
                print(f"Attempt {attempt} failed: {e}. Retrying after {wait_time} seconds...")
                time.sleep(wait_time)


def get_model_response(prompt, model="deepseek-r1-250120"):
    """
    Wrapper function to fetch a response from the model API with a given prompt.
    """
    # API base URL and API key
    # model = 'deepseek-v3-241226'
    url = "https://ark.cn-beijing.volces.com/api/v3"
    api_key = ""
    
    # Initialize the proxy to make API calls
    proxy = OpenAIApiProxy(api_key=api_key, api_base_url=url)
    
    # Fetch the response from the model API
    response = proxy.call(model, system_prompt='', user_prompt=prompt, max_tokens=8196)
    
    if isinstance(response, str):
        return response
    
    # Extract the generated content from the response
    gpt_result = response['choices'][0]['message']['content'].strip()
    return gpt_result
