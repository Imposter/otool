from requests import Session
from urllib import parse as url

class Transport(object):
    _session = None

    def __init__(self):
        self._session = Session()

    def _res_update(self, response):
        # Update URLs when there were redirects
        new_url = response.url
        for resp in response.history:
            location = resp.headers["Location"]
            resp_url = url.urlparse(resp.url)
            new_url = f"{resp_url.scheme}://{resp_url.netloc}{location}"

            resp.url = new_url

        response.url = new_url

    def get(self, *args, **kwargs):
        response = self._session.get(*args, **kwargs)
        self._res_update(response)
        
        return response

    def post(self, *args, **kwargs):
        response = self._session.post(*args, **kwargs)
        self._res_update(response)
        
        return response