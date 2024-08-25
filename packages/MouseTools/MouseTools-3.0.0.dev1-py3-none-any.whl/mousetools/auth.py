import typing
import requests
from datetime import datetime, timedelta


class Authentication:
    def __init__(self):
        self.time_of_expire: typing.Optional[datetime] = None
        self.access_token: typing.Optional[str] = None

    @staticmethod
    def authenticate() -> typing.Tuple[str, int]:
        """Gets an access token from Disney and the token's expiration time

        Returns:
            (typing.Tuple[str, int]): Access token to the api and how long until it expires
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Proxy-Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate",
        }
        response = requests.get(
            "https://disneyworld.disney.go.com/authentication/get-client-token",
            headers=headers,
            timeout=10,
        )
        auth = response.json()

        return auth["access_token"], int(auth["expires_in"])

    def get_headers(self) -> typing.Dict[str, str]:
        """Creates the headers to send during the request

        Returns:
            (typing.Dict[str, str]): Headers for the request
        """

        if self.time_of_expire is None or (datetime.now() > self.time_of_expire):
            access_token, expires_in = self.authenticate()
            self.time_of_expire = datetime.now() + timedelta(seconds=(expires_in - 10))
            self.access_token = access_token

        headers = {
            "Authorization": f"BEARER {self.access_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "*/*",
        }

        return headers


auth_obj = Authentication()
