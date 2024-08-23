from time import sleep
from typing import Any, Iterator, Optional

import requests

from ....utils import format_date, yesterday
from ....utils.client.api import DEFAULT_TIMEOUT_S, HttpMethod
from ..assets import SodaAsset
from .credentials import SodaCredentials
from .endpoints import SodaEndpointFactory

_REPORTING_PAGE_SIZE = 400
_CLOUD_PAGE_SIZE = 100
_REQUESTS_PER_MINUTE = 10
_SECONDS_PER_MINUTE = 60
_RATE_LIMIT_S = (_SECONDS_PER_MINUTE // _REQUESTS_PER_MINUTE) + 1


class SodaClient:
    def __init__(
        self,
        credentials: SodaCredentials,
    ):
        self._timeout = DEFAULT_TIMEOUT_S
        self._reporting_headers = credentials.reporting_headers
        self._auth = (credentials.api_key, credentials.secret)

    def _call(
        self,
        url: str,
        headers: dict,
        method: HttpMethod = "GET",
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        auth: Optional[tuple] = None,
    ) -> Any:
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            json=data,
            timeout=self._timeout,
            auth=auth,
        )
        response.raise_for_status()

        return response.json()

    def _get_results_paginated(self, url: str, additional: dict) -> Iterator:
        page_number = 1
        next_page = True
        while next_page:
            json_data = {
                **{"page": page_number, "size": _REPORTING_PAGE_SIZE},
                **additional,
            }
            _check_results_page = self._call(
                url=url,
                method="POST",
                data=json_data,
                headers=self._reporting_headers,
            )
            yield from _check_results_page["data"]

            next_page = len(_check_results_page["data"]) == _REPORTING_PAGE_SIZE
            page_number += 1

    def _datasets(self) -> Iterator[dict]:
        url = SodaEndpointFactory.datasets()
        next_page = True
        page_number = 0
        while next_page:
            data = self._call(
                url=url,
                method="GET",
                headers={},
                params={"size": _CLOUD_PAGE_SIZE, "page": page_number},
                auth=self._auth,
            )
            yield from data["content"]
            next_page = not data["last"]
            page_number += 1
            sleep(_RATE_LIMIT_S)

    def _check_results(self) -> Iterator:
        url = SodaEndpointFactory.check_results()
        _date = format_date(timestamp=yesterday())
        return self._get_results_paginated(
            url, additional={"from_datetime": _date}
        )

    def fetch(self, asset: SodaAsset) -> Iterator[dict]:
        if asset == SodaAsset.DATASETS:
            yield from self._datasets()
        if asset == SodaAsset.CHECK_RESULTS:
            yield from self._check_results()
        raise ValueError(f"The asset {asset}, is not supported")
