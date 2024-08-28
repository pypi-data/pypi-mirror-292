import argparse
from pathlib import Path


def create_cli_parser() -> argparse.ArgumentParser:
    """Create the CLI argparse for the pretty_print_hydra package."""
    parser = argparse.ArgumentParser(description="Pretty print Hydra config.")
    parser.add_argument("config_file", help="The Hydra config file to pretty-print.", type=Path)
    parser.add_argument(
        "overrides", help="Any overrides to apply to the config file.", nargs=argparse.ZERO_OR_MORE
    )
    parser.add_argument(
        "--no-remove-hydra-key",
        help="Do not remove the hydra key from the config.",
        action="store_true",
    )
    return parser
