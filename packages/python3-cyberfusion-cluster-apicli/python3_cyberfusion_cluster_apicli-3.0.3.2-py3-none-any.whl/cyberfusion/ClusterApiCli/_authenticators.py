import datetime
from typing import Tuple

from cached_property import cached_property

from cyberfusion.ClusterApiCli._calls import ClusterApiCall
from cyberfusion.ClusterApiCli._constants import METHOD_POST
from cyberfusion.ClusterApiCli._interfaces import AuthenticatorInterface


class ClusterApiAPIKey(AuthenticatorInterface):
    """Retrieve API key."""

    def __init__(self, server_url: str, api_key: str):
        """Construct API request to get authentication data."""
        self._server_url = server_url
        self.api_key = api_key

    @property
    def server_url(self) -> str:
        """Get server URL."""
        return self._server_url

    @property
    def header(self) -> Tuple[str, str]:
        """Get authentication header."""
        return "X-API-Key", self.api_key


class ClusterApiJWTToken(AuthenticatorInterface):
    """Retrieve API JWT token."""

    def __init__(self, server_url: str, username: str, api_key: str):
        """Construct API request to get authentication data."""
        self._server_url = server_url
        self.username = username
        self.api_key = api_key

        self.expires_at: datetime.datetime = (
            datetime.datetime.utcnow()
            + datetime.timedelta(seconds=self._jwt_token["expires_in"])
        )

    @property
    def server_url(self) -> str:
        """Get server URL."""
        return self._server_url

    @cached_property
    def _jwt_token(self) -> dict:
        """Get JWT token endpoint result."""
        call = ClusterApiCall(
            method=METHOD_POST,
            server_url=self.server_url,
            path="/api/v1/login/access-token",
            data={"username": self.username, "password": self.api_key},
        )
        call.execute()
        call.check()

        return call.response

    @property
    def token(self) -> str:
        """Get JWT token."""
        return self._jwt_token["access_token"]

    @property
    def type(self) -> str:
        """Get JWT token type."""
        return self._jwt_token["token_type"]

    @property
    def header(self) -> Tuple[str, str]:
        """Get authentication header."""
        return "Authorization", self.type + " " + self.token
