from typing import TypedDict


__all__: list[str] = ["HittingStats", "PitchingStats", "StatCast"]


HittingStats = TypedDict(
    "HittingStats",
    {
        "Age": int,
        "Pitches": int,
        "Batted Balls": int,
        "Barrels": int,
        "Barrel %": float,
        "Barrel/PA": float,
        "Exit Velocity": float,
        "Max EV": float,
        "Launch Angle": float,
        "LA Sweet-Spot %": float,
        "XBA": float,
        "XSLG": float,
        "WOBA": float,
        "XWOBA": float,
        "XWOBACON": float,
        "HardHit%": float,
        "K%": float,
        "BB%": float,
        "ERA": float,
        "xERA": float,
    },
    total=False,
)


PitchingStats = TypedDict(
    "PitchingStats",
    {
        "Tm": str,
        "LG": str,
        "BF": int,
        "W": int,
        "L": int,
        "ERA": float,
        "G": int,
        "GS": int,
        "SV": int,
        "IP": float,
        "H": int,
        "R": int,
        "ER": int,
        "HR": int,
        "BB": int,
        "SO": int,
        "WHIP": float,
    },
    total=False,
)


class StatCast(TypedDict):
    hitting: dict[str, HittingStats]
    pitching: dict[str, PitchingStats]
