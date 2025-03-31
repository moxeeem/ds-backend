import logging
import requests
from requests.exceptions import RequestException, Timeout, HTTPError


class ImageProviderError(Exception):
    pass


class ImageProviderTimeout(ImageProviderError):
    pass


class ImageNotFoundError(ImageProviderError):
    pass


logger = logging.getLogger(__name__)


class ImageProviderClient:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url
        self.timeout = timeout

    def get_image(self, image_id):
        url = f'{self.base_url}/images/{image_id}'
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except HTTPError as e:
            if response.status_code == 404:
                raise ImageNotFoundError(f'Image {image_id} not found') from e
            else:
                raise ImageProviderError(f'HTTP error {response.status_code}') from e
        except Timeout:
            raise ImageProviderTimeout('Image provider request timed out')
        except RequestException as e:
            raise ImageProviderError(f'Request error: {e}') from e
