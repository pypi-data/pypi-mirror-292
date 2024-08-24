from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
import os
from typing import TYPE_CHECKING, ClassVar, Literal, Mapping, overload
import bs4
import httpx
from bs4 import BeautifulSoup
from .types import HittingStats, PitchingStats

if TYPE_CHECKING:
    from .. import Player


@dataclass
class Client:
    player: Player

    TIMEOUT: ClassVar[str | None] = os.getenv("HTTPX_TIMEOUT")

    @cached_property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self._download_stats(), "html.parser")

    def _download_stats(self) -> bytes:
        resp: httpx.Response = httpx.get(
            self.player.url, timeout=float(self.TIMEOUT) if self.TIMEOUT else None
        )
        resp.raise_for_status()
        return resp.content

    def get_pitching(self) -> dict[str, PitchingStats]:
        stats: dict[str, PitchingStats] = {}
        statcast: bs4.Tag | None = self.soup.select_one("div#pitchingStandard table")
        if statcast:
            stats = self._get_statcast_values(statcast, type="pitching")
        return stats

    def get_hitting(self) -> dict[str, HittingStats]:
        stats: dict[str, HittingStats] = {}
        statcast: bs4.Tag | None = self.soup.select_one(
            "section#statcast-rankings table"
        )
        if statcast:
            stats = self._get_statcast_values(statcast, type="hitting")
        return stats

    def _get_statcast_header(self, statcast: bs4.Tag) -> list[str]:
        return [cell.text.strip() for cell in statcast.select("thead tr th")]

    @overload
    def _get_statcast_values(
        self, statcast: bs4.Tag, type: Literal["hitting"]
    ) -> dict[str, HittingStats]: ...

    @overload
    def _get_statcast_values(
        self, statcast: bs4.Tag, type: Literal["pitching"]
    ) -> dict[str, PitchingStats]: ...

    def _get_statcast_values(
        self, statcast: bs4.Tag, type: Literal["hitting"] | Literal["pitching"]
    ) -> Mapping[str, HittingStats | PitchingStats]:
        stats: dict[str, HittingStats | PitchingStats] = {}

        for line in statcast.select("tbody tr"):
            year_stats: dict[str, str] = {
                self._get_statcast_header(statcast)[cell_id]: cell.text.strip()
                for cell_id, cell in enumerate(line.select("td"))
            }
            year_stats.pop("", None)
            year: str = year_stats.pop("Season").lower()
            if year == "player" or year.endswith("seasons"):
                year = "all"
            stats[year] = self._convert_year_stats(year_stats)

        return stats

    @staticmethod
    def _convert_year_stats(year_stats: dict[str, str]) -> HittingStats | PitchingStats:
        converted: HittingStats | PitchingStats = {}
        known_keys: list[str] = list(
            (HittingStats.__annotations__ | PitchingStats.__annotations__).keys()
        )
        for key, val in year_stats.items():
            if key not in known_keys:
                continue
            if not val:
                converted[key] = 0
            elif val.isdigit():
                converted[key] = int(val)
            else:
                try:
                    converted[key] = float(val)
                except ValueError:
                    converted[key] = str(val)
        return converted
