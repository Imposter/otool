import os
import time
import threading

from datetime import datetime, timedelta

from .. import origin
from lib import utils

DOWNLOAD_PART_SIZE = 1024 * 1024 * 25 # 25MB part size
DOWNLOAD_CHUNK_SIZE = 1024 * 1024 # 1MB

class Download(object):
    def __init__(self, session, product_id, file_path):
        self._session = session
        self._product_id = product_id
        self._path = file_path

        self._file = open(file_path, "ab")
        self._offset = os.path.getsize(file_path)

        # Get download info
        self._url = ""
        self._expiry = datetime.utcnow()
        self._size = 0

        self._get_download_info()

    @property
    def product_id(self):
        return self._product_id

    @property
    def path(self):
        return self._path

    @property
    def running(self):
        return self._running

    @property
    def size(self):
        return self._size

    @property
    def offset(self):
        return self._offset

    def _get_download_size(self, download_url):
        # Get download size
        response = self._session._get(download_url,
            use_token=True,
            headers={
                "Range": "bytes=0-0"
            }
        )

        return int(response.headers["Content-Range"].split('/')[1])

    def _get_download_info(self):
        response = self._session._get(origin.API_ECOMMERCE_DOWNLOAD_URL,
            use_token=True,
            params={
                "productId": self._product_id
            },
            headers={
                "Accept": "application/json",
                "localeInfo": "en-US"
            }
        )

        info = utils.json_decode(response.text)

        self._url = info["url"]
        self._expiry = datetime.strptime(info["validPeriod"]["endTime"], "%Y-%m-%dT%H:%M:%SZ")
        self._size = self._get_download_size(self._url)

    def start(self):
        self._url = None

        # Get download information
        while self._offset != self._size:
            # Check if the download is valid, otherwise update the data we have on it
            current_time = datetime.utcnow()
			
            if self._url is None or (self._expiry - current_time) < timedelta(minutes=1): # 1 minute buffer
                # Get the new data
                current_size = self._size
                self._get_download_info()
                
                # Reset download if the remote version is different than the local version
                if current_size != self._size:
                    os.remove(self._path)
                    raise Exception("Remote version of the file is different than local version")

            # Calculate part size
            part_start = self._offset
            part_end = part_start + DOWNLOAD_PART_SIZE
            if part_end > self._size:
                part_end = self._size

            # Download the part
            response = self._session._get(self._url, 
                stream=True,
                headers={
                    "Range": f"bytes={part_start}-{part_end}",
                    "Connection": "keep-alive"
                }
            )

            # Write the part to a file
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                if chunk: # Filter out keep-alive chunks
                    self._file.write(chunk)

                    # Update offset
                    chunk_size = len(chunk)
                    self._offset += chunk_size

                    # Yield progress
                    yield chunk_size

class DownloadService(object):
    def __init__(self, session):
        self._session = session    

    def get_offer_update(self, product_id):
        updates = self._session._get(origin.API_ECOMMERCE_OFFER_UPDATE_URL,
            params={
                "offerIds": product_id
            },
            headers={
                "Accept": "application/json"
            }
        )

        return utils.json_decode(updates.text)

    def create_download(self, product_id, target_path):
        product_id_clean = product_id.replace(":", "_")
        file_path = os.path.join(target_path, f"{product_id_clean}.zip")
        return Download(self._session, product_id, file_path)
