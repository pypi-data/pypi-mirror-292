"""Calls."""

from typing import Dict, Optional, Union

import certifi
import requests
from cached_property import cached_property
from requests.adapters import HTTPAdapter, Retry

from cyberfusion.ClusterApiCli._constants import (
    METHOD_DELETE,
    METHOD_GET,
    METHOD_PATCH,
    METHOD_POST,
    METHOD_PUT,
)
from cyberfusion.ClusterApiCli._interfaces import AuthenticatorInterface
from cyberfusion.ClusterApiCli.exceptions import ClusterApiCallException


class ClusterApiCall:
    """Construct, execute and check API call."""

    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_NAME_HEADER = "content-type"

    HTTP_CODE_BAD_REQUEST = 400

    TIMEOUT_REQUEST = 60

    def __init__(
        self,
        method: str,
        server_url: str,
        path: str,
        authenticator: Optional[AuthenticatorInterface] = None,
        content_type_header: Optional[str] = None,
        data: Optional[Union[dict, str]] = None,
        params: Optional[Union[dict, str]] = None,
    ) -> None:
        """Set API request attributes."""
        self.method = method
        self.server_url = server_url
        self.path = path
        self.authenticator = authenticator
        self.content_type_header = content_type_header
        self.data = data
        self.params = params

    @property
    def url(self) -> str:
        """Get request URL."""
        return "".join([self.server_url, self.path])

    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {}

        if self.authenticator:
            key, value = self.authenticator.header

            headers[key] = value

        if self.content_type_header:
            headers[self.CONTENT_TYPE_NAME_HEADER] = self.content_type_header

        return headers

    @cached_property
    def session(self) -> requests.sessions.Session:
        """Get requests session."""
        session = requests.Session()

        adapter = HTTPAdapter(
            max_retries=Retry(
                total=10,
                backoff_factor=2.5,
                allowed_methods=None,
                status_forcelist=[502, 503],
            )
        )

        session.mount(self.server_url + "/", adapter)

        return session

    def execute(self) -> None:
        """Execute API request."""
        if self.method == METHOD_GET:
            self.request = self.session.get(
                self.url,
                headers=self.headers,
                params=self.params,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

        elif self.method == METHOD_PATCH:
            self.request = self.session.patch(
                self.url,
                headers=self.headers,
                data=self.data,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

        elif self.method == METHOD_PUT:
            self.request = self.session.put(
                self.url,
                headers=self.headers,
                data=self.data,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

        elif self.method == METHOD_POST:
            self.request = self.session.post(
                self.url,
                headers=self.headers,
                data=self.data,
                params=self.params,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

        elif self.method == METHOD_DELETE:
            self.request = self.session.delete(
                self.url,
                headers=self.headers,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
            )

    def check(self) -> None:
        """Check API request status code and content type."""
        if self.request.status_code < self.HTTP_CODE_BAD_REQUEST:
            if self.request.headers[self.CONTENT_TYPE_NAME_HEADER].startswith(
                self.CONTENT_TYPE_JSON
            ):
                self.response = self.request.json()
            else:
                self.response = self.request.text
        else:
            if self.request.headers[self.CONTENT_TYPE_NAME_HEADER].startswith(
                self.CONTENT_TYPE_JSON
            ):
                raise ClusterApiCallException(
                    self.request.json(), self.request.status_code
                )
            else:
                raise ClusterApiCallException(
                    self.request.text, self.request.status_code
                )
