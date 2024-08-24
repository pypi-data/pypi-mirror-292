"""Interfaces."""

from abc import ABCMeta, abstractmethod
from typing import Tuple


class AuthenticatorInterface(metaclass=ABCMeta):
    """Interface for authenticator."""

    @property
    @abstractmethod
    def server_url(self) -> str:
        """Get server URL."""
        pass

    @property
    @abstractmethod
    def header(self) -> Tuple[str, str]:
        """Get authentication header."""
        pass
