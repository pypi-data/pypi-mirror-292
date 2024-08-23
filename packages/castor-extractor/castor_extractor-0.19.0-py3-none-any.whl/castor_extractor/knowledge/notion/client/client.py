import logging
from http import HTTPStatus
from typing import Dict, Iterator

from pydantic import ValidationError

from ....utils import RequestSafeMode, empty_iterator
from ....utils.client.api import APIClient, HttpMethod
from ..assets import NotionAsset
from .constants import (
    CASTOR_NOTION_USER_AGENT,
    NOTION_BASE_URL,
    NOTION_TIMEOUT_MS,
)
from .credentials import NotionCredentials
from .endpoints import EndpointFactory
from .pagination import PaginatedResponse

logger = logging.getLogger("__name__")

NOTION_VERSION = "2021-08-16"

VOLUME_IGNORED = 10
IGNORED_ERROR_CODES = (HTTPStatus.BAD_GATEWAY,)
NOTION_SAFE_MODE = RequestSafeMode(
    max_errors=VOLUME_IGNORED,
    status_codes=IGNORED_ERROR_CODES,
)


def _search_filter(asset: str) -> Dict[str, Dict[str, str]]:
    return {"filter": {"value": asset, "property": "object"}}


class NotionClient(APIClient):
    """Client fetching data from Notion"""

    def __init__(
        self,
        credentials: NotionCredentials,
        timeout: int = NOTION_TIMEOUT_MS,
        base_url: str = NOTION_BASE_URL,
        user_agent: str = CASTOR_NOTION_USER_AGENT,
        safe_mode: RequestSafeMode = NOTION_SAFE_MODE,
    ) -> None:
        base_headers = {
            "Notion-Version": NOTION_VERSION,
            "User-Agent": user_agent,
        }

        super().__init__(
            host=base_url,
            token=credentials.token,
            headers=base_headers,
            timeout=timeout,
            safe_mode=safe_mode,
        )

    def _request(
        self, method: HttpMethod, endpoint: str, params: dict
    ) -> Iterator[dict]:
        """
        API call to Notion:
        - If result is paginated, yield all pages
        - If not, yield only the response payload
        """
        built_url = self.build_url(self._host, endpoint)
        response_payload = self._call(
            method=method,
            url=built_url,
            params=params if params and method == "GET" else None,
            data=params if params and method == "POST" else None,
        )
        try:
            paginated_response = PaginatedResponse(**response_payload)
            yield from paginated_response.results

            if not paginated_response.has_more:
                return empty_iterator()

            yield from self._request(
                method=method,
                endpoint=endpoint,
                params=paginated_response.start_cursor,
            )

        except ValidationError:
            yield response_payload

    def _page_listing(self) -> Iterator[dict]:
        return self._request(
            method="POST",
            endpoint=EndpointFactory.search(),
            params=_search_filter("page"),
        )

    def _blocks(self, block_id: str) -> Iterator[dict]:
        return self._request("GET", EndpointFactory.blocks(block_id), {})

    def databases(self) -> Iterator[dict]:
        return self._request(
            method="POST",
            endpoint=EndpointFactory.search(),
            params=_search_filter("database"),
        )

    def recursive_blocks(self, block_id: str) -> Iterator[dict]:
        """Fetch recursively all children blocks of a given block or page"""
        blocks = self._blocks(block_id)
        for block in blocks:
            if block["has_children"] and block.get("type") != "child_page":
                children = self.recursive_blocks(block["id"])
                block["child_blocks"] = list(children)

            yield block

    def pages(self) -> Iterator[dict]:
        """Fetch all pages with its whole content"""
        pages = list(self._page_listing())
        logger.info(f"Extracting {len(pages)} pages ...")
        for page in pages:
            if page.get("object") == "database":
                # Notion Search API filter for page doesn't work
                continue
            content = list(self.recursive_blocks(page["id"]))
            page["child_blocks"] = content
            yield page

    def users(self) -> Iterator[dict]:
        """Fetch all users"""
        return self._request("GET", EndpointFactory.users(), {})

    def fetch(self, asset: NotionAsset) -> Iterator[dict]:
        """Returns the needed metadata for the queried asset"""
        if asset == NotionAsset.PAGES:
            yield from self.pages()

        elif asset == NotionAsset.DATABASES:
            yield from self.databases()

        elif asset == NotionAsset.USERS:
            yield from self.users()

        else:
            raise ValueError(f"This asset {asset} is unknown")
