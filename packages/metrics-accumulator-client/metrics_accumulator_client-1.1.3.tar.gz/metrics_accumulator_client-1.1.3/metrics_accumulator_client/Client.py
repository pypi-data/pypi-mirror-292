import requests

from prometheus_client import CollectorRegistry, exposition
from requests import Response


class ClientResponse:
    def __init__(self, request_response: Response):
        self.request_response = request_response
        self.status_code = request_response.status_code
        self.content = request_response.content

class Client():
    def __init__(self, url: str, x_api_key=None):
        if url is None or url.strip() == "":
            raise "url cannot be null or empty"
        self.url = strip_forward_slash(url)
        self.x_api_key = x_api_key

    def update_metrics(self, metric_group: str, registry: CollectorRegistry) -> ClientResponse:
        if self.x_api_key is None:
            raise "x-api-key is not set"
        url = f'{self.url}/update/{metric_group}'
        data = exposition.generate_latest(registry).decode()
        res = requests.post(url=url, data=data, headers={"Content-Type": "text/plain", "x-api-key": self.x_api_key})
        return ClientResponse(res)


    def get_metric_group(self, metric_group: str) -> ClientResponse:
        url = f'{self.url}/metrics/{metric_group}'
        res = requests.get(url=url)
        return ClientResponse(res)

    def reload_configurations(self) -> ClientResponse:
        url = f'{self.url}/reload-configuration'
        res = requests.put(url=url)
        return ClientResponse(res)

    def reset_metric_group(self, metric_group) -> ClientResponse:
        url = f'{self.url}/reset-metric-group/{metric_group}'
        res = requests.put(url=url)
        return ClientResponse(res)

    def service_discovery(self) -> ClientResponse:
        url = f'{self.url}/service-discovery'
        res = requests.get(url=url)
        return ClientResponse(res)

    def current_configurations(self) -> ClientResponse:
        url = f'{self.url}/current-configurations'
        res = requests.get(url=url)
        return ClientResponse(res)

def strip_forward_slash(s: str):
    if s is None or len(s) == 0 or s[len(s)-1] != '/':
      return s
    return strip_forward_slash(s[0: len(s)-1])