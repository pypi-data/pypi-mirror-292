from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar
import httpx
from bs4 import BeautifulSoup


@dataclass
class Player:

    SEP: ClassVar[str] = ", "
    BASE_URL: ClassVar[str] = "https://baseballsavant.mlb.com/savant-player/"

    def __init__(self, id: str, fullname: str) -> None:
        if self.SEP not in fullname:
            raise ValueError("Not a player")
        self.id: int = int(id)
        self.fullname: str = fullname

    @property
    def firstname(self) -> str:
        return self.fullname.split(self.SEP)[-1]

    @property
    def lastname(self) -> str:
        return self.fullname.split(self.SEP)[0]

    @property
    def slug(self) -> str:
        return "-".join([self.firstname, self.lastname, str(self.id)]).lower()

    @property
    def url(self) -> str:
        return f"{self.BASE_URL}{self.slug}"

    @cached_property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self._download_stats(), "html.parser")

    def _download_stats(self) -> bytes:
        resp: httpx.Response = httpx.get(self.url)
        resp.raise_for_status()
        return resp.content

    def __repr__(self) -> str:
        return (
            f'<Player(id={self.id}, lastname="{self.lastname}", '
            f'firstname="{self.firstname}")>'
        )
