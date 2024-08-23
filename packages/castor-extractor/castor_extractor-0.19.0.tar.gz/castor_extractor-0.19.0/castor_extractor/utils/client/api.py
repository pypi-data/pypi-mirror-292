import logging
from typing import Any, Callable, Dict, Literal, Optional

import requests

from ...types import ExternalAsset
from ..safe_request import RequestSafeMode, handle_response

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_S = 30

# https://requests.readthedocs.io/en/latest/api/#requests.request
HttpMethod = Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"]


def _authentication_header(token: Optional[str] = None) -> Dict[str, str]:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return dict()


class APIClient:
    """
    API client
    - authentication via access token
    """

    def __init__(
        self,
        host: str,
        token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT_S,
        safe_mode: RequestSafeMode = RequestSafeMode(),
    ):
        self._host = host
        self._token = token or ""
        self._timeout = timeout
        self._base_headers = headers or {}
        self.safe_mode = safe_mode

    @staticmethod
    def build_url(host: str, path: str):
        if not host.startswith("https://"):
            host = "https://" + host
        return f"{host.strip('/')}/{path}"

    @property
    def _headers(self):
        """Returns specified headers and authentication headers altogether"""
        return {**self._base_headers, **_authentication_header(self._token)}

    def _call(
        self,
        url: str,
        method: HttpMethod = "GET",
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        processor: Optional[Callable] = None,
    ) -> Any:
        logger.debug(f"Calling {method} on {url}")
        response = requests.request(
            method,
            url,
            headers=self._headers,
            params=params,
            json=data,
            timeout=self._timeout,
        )
        response_payload = handle_response(response, self.safe_mode)

        if processor:
            return processor(response)

        return response_payload

    def get(
        self,
        path: str,
        payload: Optional[dict] = None,
        processor: Optional[Callable] = None,
    ) -> dict:
        """path: REST API operation path, such as /api/2.0/clusters/get"""
        url = self.build_url(self._host, path)
        return self._call(url=url, data=payload, processor=processor)
