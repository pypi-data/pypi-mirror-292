# PyLich

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/georgeholt1/pylich/unit_tests.yml)
![PyPI - Version](https://img.shields.io/pypi/v/pylich)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pylich)
![GitHub License](https://img.shields.io/github/license/georgeholt1/pylich)

A super simple Python utility to check for dead links in a website.

## Installation

PyLich is available on [PyPI](https://pypi.org/project/pylich/) and can be installed using [pip](https://pip.pypa.io/en/stable/):

```bash
pip install pylich
```

## Usage

Simply provide the URL of the sitemap and `pylich` will crawl through links in the pages and check their status. `pylich` can be used as a command line tool or as a Python package.

### Command Line

```bash
pylich https://www.example.com/sitemap.xml
```

The command will exit with a status code of 1 if any dead links are found and 0 otherwise.

#### Options

| Flag | Arguments | Description |
| --- | --- | --- |
| `-v` | N/A | Verbose mode. Print progress to the console as well as a summary of the dead links at the end. |
| `-i` | List of integer HTTP response codes | Ignore links with the specified HTTP response codes. |

```bash
pylich https://www.example.com/sitemap.xml -v -i 404 500
```

### Python Package

PyLich can also be used as a Python package. 

```python
from pylich import LinkChecker
checker = LinkChecker(
    "https://www.example.com/sitemap.xml",
    verbose=True,
    ignored_status_codes=[404, 500]
)
urls = checker.get_sitemap_urls()
broken_links = checker.check_links(urls)
checker.print_dead_links()
```

## Contributing

Pull requests are welcome.

Package and dependency management is done using [Poetry](https://python-poetry.org/). To install the dependencies and the package in development mode, run:

```bash
poetry install
```

To run the tests, run:

```bash
pytest
```

Pre-commit hooks are available to run code formatting and linting. To install the hooks, run:

```bash
pre-commit install
```