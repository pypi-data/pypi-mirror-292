from . import Players


def main() -> None:
    """Main function"""
    players: Players = Players()
    players.fetch()
    print(players.guerrero)


if __name__ == "__main__":
    main()
