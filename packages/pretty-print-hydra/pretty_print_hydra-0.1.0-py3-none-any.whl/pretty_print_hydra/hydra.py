from pathlib import Path

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig, open_dict, read_write


def remove_hydra_key_from_config(config: DictConfig) -> DictConfig:
    """Remove the hydra key from a Hydra config.

    This is needed when we are going to resolve the config without being within a run because it
    will fail otherwise.
    """
    with read_write(config), open_dict(config):
        config["hydra"] = None
    return config


def load_hydra_config(
    config_dir: Path,
    config_file_name: str,
    overrides: list[str] | None = None,
    *,
    hydra_version_base: str = "1.3",
    should_remove_hydra_key_from_config: bool = True,
) -> DictConfig:
    """Load a Hydra config file and return it."""
    if overrides is None:
        overrides = []

    with hydra.initialize_config_dir(
        config_dir=str(config_dir.resolve()), version_base=hydra_version_base
    ):
        config = hydra.compose(
            config_name=config_file_name, return_hydra_config=True, overrides=overrides
        )
        HydraConfig.instance().set_config(config)

    if should_remove_hydra_key_from_config:
        config = remove_hydra_key_from_config(config)

    return config
