"""Exceptions."""

from dataclasses import dataclass


@dataclass
class ClusterApiCallException(Exception):
    """API call failed."""

    body: str
    status_code: int


class MultipleAuthenticatorsMatchError(Exception):
    """Multiple authenticators match."""

    pass
