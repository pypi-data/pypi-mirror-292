from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar
from .baseball_savant import Client, HittingStats, PitchingStats, StatCast


@dataclass
class Player:

    SEP: ClassVar[str] = ", "
    BASE_URL: ClassVar[str] = "https://baseballsavant.mlb.com/savant-player/"

    def __init__(self, id: str, fullname: str) -> None:
        if self.SEP not in fullname:
            raise ValueError("Not a player")
        self.id: int = int(id)
        self.fullname: str = fullname
        self.client: Client = Client(self)

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
    def statcast(self) -> StatCast:
        return {"hitting": self.hitting, "pitching": self.pitching}

    @cached_property
    def pitching(self) -> dict[str, PitchingStats]:
        return self.client.get_pitching()

    @cached_property
    def hitting(self) -> dict[str, HittingStats]:
        return self.client.get_hitting()

    def __repr__(self) -> str:
        return (
            f'<Player(id={self.id}, lastname="{self.lastname}", '
            f'firstname="{self.firstname}")>'
        )
