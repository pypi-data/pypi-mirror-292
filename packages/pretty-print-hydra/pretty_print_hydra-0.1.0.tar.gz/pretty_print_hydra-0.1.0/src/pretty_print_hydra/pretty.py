from pathlib import Path
from typing import Any

from omegaconf import DictConfig, OmegaConf
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


def prettyify_inputs(
    config_file: Path,
    overrides: list[str],
    *,
    config_file_prefix: str = "config_file = ",
    override_prefix: str = "overrides = ",
    panel_kwargs: dict[str, Any] | None = None,
) -> Panel:
    """Make the inputs to the confile file pretty."""
    # Make the prefixes
    override_prefix = f"{(len(config_file_prefix) - len(override_prefix)) * ' '}{override_prefix}"

    # Pretty the config file
    printed_config_file = f"{config_file_prefix}'{config_file}'"

    # Pretty the overrides
    printed_overrides = []
    if overrides:
        printed_overrides = [" " * len(override_prefix) + override for override in overrides]
        printed_overrides[0] = override_prefix + printed_overrides[0].lstrip()

    renderable = printed_config_file
    if printed_overrides:
        renderable += "\n" + "\n".join(printed_overrides)

    # Make the panel
    return Panel(
        renderable,
        title="inputs",
        border_style="yellow",
        highlight=True,
        expand=False,
        **(panel_kwargs or {}),
    )


def prettyify_hydra_config(
    config: DictConfig, *, syntax_kwargs: dict[str, Any] | None = None
) -> Syntax:
    """Parse and resolve a Hydra config, and then pretty-print it."""
    # Resolve the Hydra config
    config_as_yaml = OmegaConf.to_yaml(config, resolve=True)
    # Make the syntax
    return Syntax(
        config_as_yaml,
        "yaml",
        theme="ansi_dark",
        indent_guides=True,
        dedent=True,
        tab_size=2,
        line_numbers=True,
        **(syntax_kwargs or {}),
    )


def pretty_print_config(pretty_inputs: Panel, pretty_config: Syntax) -> None:
    """Print the pretty inputs and pretty config."""
    console = Console()
    console.rule("Current config")

    console.print(pretty_inputs, markup=True, highlight=True)
    console.print(pretty_config, markup=True, highlight=True)

    console.rule()
