"""Helper classes to execute Core API calls."""

import configparser
import datetime
import json
from typing import Optional, Union

from cached_property import cached_property

from cyberfusion.ClusterApiCli._authenticators import (
    ClusterApiAPIKey,
    ClusterApiJWTToken,
)
from cyberfusion.ClusterApiCli._calls import ClusterApiCall
from cyberfusion.ClusterApiCli._constants import (
    METHOD_DELETE,
    METHOD_GET,
    METHOD_PATCH,
    METHOD_POST,
    METHOD_PUT,
)
from cyberfusion.ClusterApiCli._interfaces import AuthenticatorInterface
from cyberfusion.ClusterApiCli.api_user_info import APIUserInfo
from cyberfusion.ClusterApiCli.exceptions import (  # noqa: F401
    ClusterApiCallException,
    MultipleAuthenticatorsMatchError,
)
from cyberfusion.Common.Config import CyberfusionConfig


class ClusterApiRequest:
    """Prepare API request and call ClusterApiCall."""

    SECTION_CONFIG = "clusterapi"

    KEY_CONFIG_SERVER_URL = "serverurl"
    KEY_CONFIG_USERNAME = "username"
    KEY_CONFIG_API_KEY = "apikey"
    KEY_CONFIG_PASSWORD = "password"

    def __init__(self, config_file_path: Optional[str] = None) -> None:
        """Construct API request."""
        self.config_file_path = config_file_path

        self.server_url = self.config.get(
            self.SECTION_CONFIG, self.KEY_CONFIG_SERVER_URL
        )

        self.data: Optional[Union[dict, str]] = None
        self.params: Optional[Union[dict, str]] = None
        self.content_type_header: Optional[str] = None
        self._authenticator: Optional[AuthenticatorInterface] = None

    @cached_property
    def config(self) -> CyberfusionConfig:
        """Get config."""
        return CyberfusionConfig(path=self.config_file_path)

    @property
    def username(self) -> Optional[str]:
        """Get username."""
        try:
            return self.config.get(
                self.SECTION_CONFIG, self.KEY_CONFIG_USERNAME
            )
        except configparser.NoOptionError:
            return None

    @property
    def password(self) -> Optional[str]:
        """Get password."""
        try:
            return self.config.get(
                self.SECTION_CONFIG, self.KEY_CONFIG_PASSWORD
            )
        except configparser.NoOptionError:
            return None

    @property
    def api_key(self) -> Optional[str]:
        """Get API key."""
        try:
            return self.config.get(
                self.SECTION_CONFIG, self.KEY_CONFIG_API_KEY
            )
        except configparser.NoOptionError:
            return None

    @property
    def api_user_info(self) -> "APIUserInfo":
        """Get API user information."""
        return APIUserInfo(self.authenticator)

    @property
    def authenticator(self) -> AuthenticatorInterface:
        """Get authenticator object."""
        if (self.username and self.password) and self.api_key:
            raise MultipleAuthenticatorsMatchError

        if self.username and self.password:
            if (not self._authenticator) or (
                datetime.datetime.utcnow() > self._authenticator.expires_at
            ):
                self._authenticator = ClusterApiJWTToken(
                    self.server_url, self.username, self.password
                )
        elif self.api_key:
            if not self._authenticator:
                self._authenticator = ClusterApiAPIKey(
                    self.server_url, self.api_key
                )

        return self._authenticator

    def GET(self, path: str, data: Optional[dict] = None) -> None:
        """Set API GET request."""
        self.method = METHOD_GET
        self.path = path
        self.params = data
        self.content_type_header = None  # Use default

    def PATCH(self, path: str, data: dict) -> None:
        """Set API PATCH request."""
        self.method = METHOD_PATCH
        self.path = path
        self.data = json.dumps(data)
        self.content_type_header = ClusterApiCall.CONTENT_TYPE_JSON

    def PUT(self, path: str, data: dict) -> None:
        """Set API PUT request."""
        self.method = METHOD_PUT
        self.path = path
        self.data = json.dumps(data)
        self.content_type_header = ClusterApiCall.CONTENT_TYPE_JSON

    def POST(
        self, path: str, data: dict, params: dict = {}  # noqa: B006
    ) -> None:
        """Set API POST request."""
        self.method = METHOD_POST
        self.path = path
        self.data = json.dumps(data)
        self.params = params
        self.content_type_header = ClusterApiCall.CONTENT_TYPE_JSON

    def DELETE(self, path: str) -> None:
        """Set API DELETE request."""
        self.method = METHOD_DELETE
        self.path = path
        self.data = None
        self.content_type_header = None  # Use default

    def execute(self) -> dict:
        """Handle API request with ClusterApiCall."""
        call = ClusterApiCall(
            method=self.method,
            server_url=self.server_url,
            path=self.path,
            authenticator=self.authenticator,
            content_type_header=self.content_type_header,
            data=self.data,
            params=self.params,
        )

        call.execute()
        call.check()

        return call.response
