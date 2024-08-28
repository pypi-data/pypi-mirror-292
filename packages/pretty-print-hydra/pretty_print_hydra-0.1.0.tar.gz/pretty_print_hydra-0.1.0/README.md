# pretty-print-hydra

[![PyPI version](https://badge.fury.io/py/pretty-print-hydra.svg)](https://badge.fury.io/py/pretty-print-hydra)
[![Python Version](https://img.shields.io/pypi/pyversions/pretty-print-hydra.svg)](https://pypi.org/project/pretty-print-hydra/)
[![Downloads](https://pepy.tech/badge/pretty-print-hydra)](https://pepy.tech/project/pretty-print-hydra)

Test coverage
CI status
Release Method (semver)

This is a simple package that has the simple job of just pretty-printing a hydra config. It is useful for debugging and understanding the structure of a hydra config, and making sure that the overrides and changed you make are being applied.

## Installation

```bash
pip install pretty-print-hydra
```

## Usage Example

```bash
python -m pretty_print_hydra config/train.yaml seed=2 +foo=bar ~remove_this_one
```

This will print the config in a pretty format, with the overrides applied too. That's it.

## License

MIT
