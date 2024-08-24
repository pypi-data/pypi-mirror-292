"""API user info."""

from typing import List, Optional

from cyberfusion.ClusterApiCli import ClusterApiCall
from cyberfusion.ClusterApiCli._constants import METHOD_POST
from cyberfusion.ClusterApiCli._interfaces import AuthenticatorInterface


class APIUserInfo:
    """Container for information about authenticated API user."""

    def __init__(self, authenticator: "AuthenticatorInterface") -> None:
        """Set attributes."""
        self.authenticator = authenticator

    def _get(self) -> dict:
        """Get test-token endpoint result."""
        call = ClusterApiCall(
            method=METHOD_POST,
            server_url=self.authenticator.server_url,
            path="/api/v1/login/test-token",
            authenticator=self.authenticator,
        )
        call.execute()
        call.check()

        return call.response

    @property
    def clusters_ids(self) -> List[int]:
        """Get IDs of clusters that this API user has access to."""
        return self._get()["clusters"]

    @property
    def is_superuser(self) -> bool:
        """Get if API user is superuser."""
        return self._get()["is_superuser"]

    @property
    def customer_id(self) -> Optional[int]:
        """Get API user customer ID."""
        return self._get()["customer_id"]
