from .api import APIClient, _authentication_header


def test_APIClient_build_url():
    expected = "https://3.14.azuredatabricks.net/api/2.1/unity-catalog/tables"

    path = "api/2.1/unity-catalog/tables"

    host = "3.14.azuredatabricks.net"
    assert expected == APIClient.build_url(host, path)

    host_with_http = "https://3.14.azuredatabricks.net"
    assert expected == APIClient.build_url(host_with_http, path)

    host_with_trailing_slash = "https://3.14.azuredatabricks.net/"
    assert expected == APIClient.build_url(host_with_trailing_slash, path)


def test__authentication_header():
    expected_headers = {"Authorization": "Bearer my_token"}
    assert _authentication_header("my_token") == expected_headers

    assert _authentication_header("") == {}
    assert _authentication_header() == {}
