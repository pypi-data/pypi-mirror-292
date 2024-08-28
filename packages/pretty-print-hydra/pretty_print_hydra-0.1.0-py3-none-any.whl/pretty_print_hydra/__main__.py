from pretty_print_hydra.cli import create_cli_parser
from pretty_print_hydra.hydra import load_hydra_config
from pretty_print_hydra.pretty import pretty_print_config, prettyify_hydra_config, prettyify_inputs


def _enable_rich_traceback() -> None:
    """Enable rich traceback for the package.

    This is useful for debugging and seeing the full traceback in a more readable format.
    """
    from rich.traceback import install

    _ = install(show_locals=True)


def main() -> None:
    """Run the pretty_print_hydra package."""
    _enable_rich_traceback()
    parser = create_cli_parser()
    args = parser.parse_args()

    config = load_hydra_config(
        config_dir=args.config_file.parent,
        config_file_name=args.config_file.name,
        overrides=args.overrides,
        # If arg.no_remove_hydra_key is true, then should_remove_hydra_key_from_config is false.
        should_remove_hydra_key_from_config=not args.no_remove_hydra_key,
    )

    pretty_inputs = prettyify_inputs(args.config_file, args.overrides)
    pretty_config = prettyify_hydra_config(config)
    pretty_print_config(pretty_inputs, pretty_config)


if __name__ == "__main__":
    main()
