# [relpath](https://github.com/jifox/relpath.git) - relative path module

![Python package](https://github.com/jifox/relpath/actions/workflows/tests.yml/badge.svg)  [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)  [![Known Vulnerabilities](https://snyk.io/test/github/jifox/relpath/badge.svg)](https://snyk.io/test/github/jifox/relpath)

This module addresses a limitation of the `pathlib.Path` class. When using `Path`, if the relative path is not a subdirectory of the base path, it raises a `ValueError`. However, with this module, that weakness is eliminated.

## Installation

```bash
pip install rel-path
```

- [View on PyPi](https://pypi.org/project/rel-path/)
- [View on GitHub](https://github.com/jifox/relpath)

## Example for error:

```python
from pathlib import Path

base="/home"
rel="/"

# Error when using Path
Path(rel).relative_to(base)

Exception has occurred: ValueError
'/' does not start with '/home'
```

## Example using relpath module:

```python
from relpath import relative_path

base="/home"
rel="/"

print(relative_path(base, rel))
../
```

## Configure PyPi API Token

[Poetry](https://python-poetry.org/) is used to manage the package.
[How to publish](https://www.digitalocean.com/community/tutorials/how-to-publish-python-packages-to-pypi-using-poetry-on-ubuntu-22-04)

To configure the PyPi API token, use the following command once:

```bash
# Run once to set the PyPi API token
set +o history
poetry config pypi-token.pypi '<your-pypi-token>'
set -o history

# Build the package
poetry build

# Publish the package
poetry publish
```



## Support

If you encounter any issues with the relpath module, please report them on GitHub. I will respond as soon as possible. Contributions to the code are always welcome, and I appreciate ideas for new modules or improvements to existing ones.


# Change Log

## [1.0.2] - 2024-08-23

### Added

- Added support for poetry
- Added Change Log to README.md

### Removed

- Support for Python 3.6, 3.7, and 3.7
