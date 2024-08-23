import sys
from collections import UserDict
from typing import Any, ClassVar, overload
import httpx
from bs4 import BeautifulSoup
from . import Player


if sys.version_info >= (3, 12):
    from typing import Self
else:
    from typing_extensions import Self


class Players(UserDict):

    BASE_URL: ClassVar[str] = "http://baseballsavant.mlb.com/"
    MLB_SEARCH: ClassVar[str] = BASE_URL + "statcast_search"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.data: dict[int, Player]
        self._by_slug: dict[str, Player] = {}
        super().__init__(self, *args, **kwargs)

    def fetch(self) -> Self:
        home: httpx.Response = httpx.get(self.MLB_SEARCH, follow_redirects=True)
        home.raise_for_status()
        return self._parse_bs4(BeautifulSoup(home.content, "html.parser"))

    def _parse_bs4(self, soup: BeautifulSoup) -> Self:
        for player in soup.find_all("option"):
            try:
                self.add(
                    Player(
                        id=player.attrs["value"],
                        fullname=player.text.strip().split("\n")[-1].strip(),
                    )
                )
            except (KeyError, ValueError):
                continue
        return self

    def add(self, player: Player) -> Self:
        self.data[player.id] = player
        self._by_slug[player.slug] = player
        return self

    def get_one(
        self,
        *,
        firstname: str = "",
        lastname: str = "",
        id: int = 0,
        strict: bool = False,
    ) -> Player | None:
        if id:
            return super().get(id)
        if firstname or lastname:
            results: list[Player] = []
            for player in self[lastname]:
                if strict and self._search_by(player, firstname, strict=True):
                    results.append(player)
                else:
                    if self._search_by(player, firstname):
                        results.append(player)
            if len(results) > 1:
                raise ValueError(f"Multiple players for the search: {len(results)}")
            elif len(results) == 1:
                return results[0]
            else:
                return None

    def get_all(
        self,
        *,
        firstname: str = "",
        lastname: str = "",
        id: int = 0,
        strict: bool = False,
    ) -> list[Player]:
        if id:
            if player := self.get_one(id=id):
                return [player]
        if firstname or lastname:
            players: list[Player] = self[lastname]
            if strict:
                return [
                    player
                    for player in players
                    if self._search_by(player, firstname, strict=True)
                ]
            return [player for player in players if self._search_by(player, firstname)]
        return []

    @staticmethod
    def _search_by(
        player: Player, value: str, *, by: str = "firstname", strict: bool = False
    ) -> bool:
        value = str(value).lower()
        player_value: str = str(getattr(player, by, "")).lower()
        if strict:
            return player_value == value
        return value in player_value or player_value in value

    @overload
    def __getitem__(self, key: int) -> Player: ...

    @overload
    def __getitem__(self, key: str) -> list[Player]: ...

    def __getitem__(self, key: int | str) -> Player | list[Player]:
        if isinstance(key, int):
            return super().__getitem__(key)
        return [player for slug, player in self._by_slug.items() if key.lower() in slug]

    @overload  # type: ignore
    def get(self, key: int) -> Player: ...

    @overload
    def get(self, key: str) -> list[Player]: ...

    def get(self, key: int | str) -> Player | list[Player]:
        return self[key]

    def __getattr__(self, key: str) -> list[Player]:
        return self.__getitem__(key)
