from unittest.mock import patch

from .client import NotionClient
from .credentials import NotionCredentials

MOCK_PAGINATED_RESPONSE = {
    "results": [{"result_id": 1}],
    "next_cursor": "2",
    "has_more": True,
}
MOCK_PAGINATED_RESPONSE_2 = {
    "results": [{"result_id": 2}],
    "next_cursor": None,
    "has_more": False,
}
MOCK_RESPONSE = {"result_id": 3}


@patch.object(NotionClient, "_call")
def test_NotionClient__request(mock_call):
    mock_call.side_effect = [
        MOCK_PAGINATED_RESPONSE,
        MOCK_PAGINATED_RESPONSE_2,
        MOCK_RESPONSE,
    ]

    client = NotionClient(NotionCredentials(token="MockToken"))
    response = list(client._request("GET", "fake_endpoint", {}))
    assert response == [{"result_id": 1}, {"result_id": 2}]

    response = list(client._request("GET", "fake_endpoint", {}))
    assert response == [{"result_id": 3}]


MOCK_BLOCK = [{"object": "block", "id": "1", "has_children": True}]
MOCK_BLOCK_CHILDREN = [
    {"object": "block", "id": "2", "has_children": False},
    {"object": "block", "id": "3", "has_children": True, "type": "child_page"},
]


@patch.object(NotionClient, "_blocks")
def test_NotionClient__recursive_blocks(mock_blocks):
    mock_blocks.side_effect = [
        MOCK_BLOCK,
        MOCK_BLOCK_CHILDREN,
    ]

    client = NotionClient(NotionCredentials(token="MockToken"))
    response = list(client.recursive_blocks("1"))

    assert response == [
        {
            "object": "block",
            "id": "1",
            "has_children": True,
            "child_blocks": [
                {"object": "block", "id": "2", "has_children": False},
                {
                    "object": "block",
                    "id": "3",
                    "has_children": True,
                    "type": "child_page",
                },
            ],
        }
    ]
