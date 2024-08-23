"""Module that defines the data class Account."""

from dataclasses import dataclass, field


@dataclass
class Account:
    """The account data class.

    Args:
        name (str): The account name.
        username (str): The login username.
        password (str): The login password.
        categories (list[str]): The account categories.
        domain (str): The login domain.
        notes (str): The optional notes.
    """

    name: str
    username: str
    password: str
    categories: list[str] = field(default=None)
    domain: str = field(default=None)
    notes: str = field(default=None)
