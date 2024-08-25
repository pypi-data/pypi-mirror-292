from mousetools import auth


def test_auth():
    token, expire = auth.auth_obj.authenticate()
    assert token
    assert expire

    headers = auth.auth_obj.get_headers()
    assert headers

    assert headers["Authorization"] == f"BEARER {token}"
