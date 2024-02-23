import sys

from seriesmgmtsystem.main.mainImpl import MainImpl


def main() -> None:
    """Entry point for the application script"""
    main = MainImpl()
    main.get_arguments(sys.argv[1:])


if __name__ == "__main__":
    main()
