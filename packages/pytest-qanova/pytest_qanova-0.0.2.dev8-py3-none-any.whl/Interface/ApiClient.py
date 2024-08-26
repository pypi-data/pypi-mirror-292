import httpx
import aiohttp
import asyncio
import logging
from urllib.parse import urljoin


class ApiClient:
    def __init__(self, base_url, token = None):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            }
        if token:
            self.headers['QaNovaToken'] = f'{token}'
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    class AsyncClient:
        def __init__(self, base_url, headers, logger):
            self.base_url = base_url
            self.headers = headers
            self.logger = logger
        
        async def get(self, endpoint, params = None):
            """Send a GET request without waiting for the response."""
            url = urljoin(self.base_url, endpoint)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    self.logger.info(f"Async GET request sent to {url} - Status: {response.status}")
        
        async def post(self, endpoint, data):
            """Send a POST request without waiting for the response."""
            url = urljoin(self.base_url, endpoint)
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data) as response:
                    self.logger.info(f"Async POST request sent to {url} - Status: {response.status}")
        
        async def put(self, endpoint, data):
            """Send a PUT request without waiting for the response."""
            url = urljoin(self.base_url, endpoint)
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=self.headers, json=data) as response:
                    self.logger.info(f"Async PUT request sent to {url} - Status: {response.status}")
        
        async def delete(self, endpoint, params = None):
            """Send a DELETE request without waiting for the response."""
            url = urljoin(self.base_url, endpoint)
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, params=params, headers=self.headers) as response:
                    self.logger.info(f"Async DELETE request sent to {url} - Status: {response.status}")
        
        def send_get(self, endpoint, params = None):
            """Convenience method to fire a GET request without blocking."""
            loop = asyncio.get_event_loop()
            loop.create_task(self.get(endpoint, params=params))
        
        def send_post(self, endpoint, data):
            """Convenience method to fire a POST request without blocking."""
            loop = asyncio.get_event_loop()
            loop.create_task(self.post(endpoint, data))
        
        def send_put(self, endpoint, data):
            """Convenience method to fire a PUT request without blocking."""
            loop = asyncio.get_event_loop()
            loop.create_task(self.put(endpoint, data))
        
        def send_delete(self, endpoint, params = None):
            """Convenience method to fire a DELETE request without blocking."""
            loop = asyncio.get_event_loop()
            loop.create_task(self.delete(endpoint, params=params))
    
    class SyncClient:
        def __init__(self, base_url, headers, logger):
            self.base_url = base_url
            self.headers = headers
            self.logger = logger
        
        def get(self, endpoint, params = None):
            """Perform a GET request and wait for the response."""
            url = urljoin(self.base_url, endpoint)
            try:
                response = httpx.get(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                self.logger.info(f"Sync GET request to {url} succeeded.")
                return response.json()
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Sync GET request to {url} failed: {e}")
                raise
        
        def post(self, endpoint, data, params=None):
            """Perform a POST request and wait for the response."""
            url = urljoin(self.base_url, endpoint)
            try:
                response = httpx.post(url, headers=self.headers, json=data, params=params, timeout=10)
                response.raise_for_status()
                self.logger.info(f"Sync POST request to {url} succeeded.")
                return response.json()
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Sync POST request to {url} failed: {e}")
                raise
        
        def put(self, endpoint, data):
            """Perform a PUT request and wait for the response."""
            url = urljoin(self.base_url, endpoint)
            try:
                response = httpx.put(url, headers=self.headers, json=data, timeout=10)
                response.raise_for_status()
                self.logger.info(f"Sync PUT request to {url} succeeded.")
                return response.json()
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Sync PUT request to {url} failed: {e}")
                raise
        
        def delete(self, endpoint, params = None):
            """Perform a DELETE request and wait for the response."""
            url = urljoin(self.base_url, endpoint)
            try:
                response = httpx.delete(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                self.logger.info(f"Sync DELETE request to {url} succeeded.")
                return response.json()
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Sync DELETE request to {url} failed: {e}")
                raise
    
    @property
    def async_(self):
        return self.AsyncClient(self.base_url, self.headers, self.logger)
    
    @property
    def sync(self):
        return self.SyncClient(self.base_url, self.headers, self.logger)

# Example usage:
# client = ApiClient(base_url='https://api.example.com', token='your_token')

# Fire-and-forget async requests
# client.async_.send_get('/resource')

# Async requests waiting for responses
# loop = asyncio.get_event_loop()
# loop.run_until_complete(client.async_.get('/resource'))

# Synchronous requests
# response = client.sync.get('/resource')
# print(response)
