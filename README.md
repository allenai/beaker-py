<div align="center">
<br>
<img src="https://raw.githubusercontent.com/allenai/beaker-py/main/docs/source/_static/beaker-500px-transparent.png" width="200"/>
<br>
<br>
<h1>beaker-py</h1>
<p>A lightweight, standalone, pure Python client for <a href="https://beaker.org">Beaker</a></p>
<hr/>
<a href="https://github.com/allenai/beaker-py/actions">
    <img alt="CI" src="https://github.com/allenai/beaker-py/workflows/Main/badge.svg?event=push&branch=main">
</a>
<a href="https://pypi.org/project/beaker-py/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/beaker-py">
</a>
<a href="https://beaker-py.readthedocs.io/en/latest/">
    <img src="https://readthedocs.org/projects/beaker-py/badge/?version=latest" alt="Documentation Status" />
</a>
<a href="https://github.com/allenai/beaker-py/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/allenai/beaker-py.svg?color=blue&cachedrop">
</a>
<br/>
</div>

## Features

<!-- start features -->

🪶 *Lightweight*

- Minimal dependencies.
- Only pure-Python dependencies.
- Communicates directly with the Beaker server via HTTP requests (Beaker CLI not required).

💪 *Robust*

- Automatically retries failed HTTP requests with exponential backoff.
- Runtime data validation.
- High test coverage.

📓 *Exhaustively-typed and documented*

- Thorough data model for all input / output types.
- Every expected HTTP error from the Beaker server is translated into a specific exception type.

<!-- end features -->

## Quick links

- [Documentation](https://beaker-py.readthedocs.io/)
- [PyPI package](https://pypi.org/project/beaker-py/)
- [Contributing](https://github.com/allenai/beaker-py/blob/main/CONTRIBUTING.md)
- [License](https://github.com/allenai/beaker-py/blob/main/LICENSE)

*See also 👇*

- [Beaker (CLI)](https://github.com/allenai/beaker)
- [Beaker Gantry](https://github.com/allenai/beaker-gantry)
- Beaker-relevant *GitHub Actions*
  - [setup-beaker](https://github.com/marketplace/actions/setup-beaker)
  - [beaker-command](https://github.com/marketplace/actions/beaker-command)
  - [beaker-run](https://github.com/marketplace/actions/beaker-run)

## Installing

### Installing with `pip`

**beaker-py** is available [on PyPI](https://pypi.org/project/beaker-py/). Just run

```bash
pip install beaker-py
```

### Installing from source

To install **beaker-py** from source, first clone [the repository](https://github.com/allenai/beaker-py):

```bash
git clone https://github.com/allenai/beaker-py.git
cd beaker-py
```

Then run

```bash
pip install -e .
```

## Quick start

<!-- start quickstart -->

If you've already configured the [Beaker command-line client](https://github.com/allenai/beaker/), **beaker-py** will 
find and use the existing configuration file (usually located at `$HOME/.beaker/config.yml`).
Otherwise just set the environment variable `BEAKER_TOKEN` to your Beaker [user token](https://beaker.org/user).

Either way, you should then instantiate the Beaker client with `.from_env()`:

```python
from beaker import Beaker

beaker = Beaker.from_env(default_workspace="my_org/my_workspace")
```

The API of **beaker-py** is meant to mirror - as closely as possible - the API of the Beaker CLI.
For example, when you do this with the CLI:

```bash
beaker dataset create --name foo .
```

The **beaker-py** equivalent would be:

```python
beaker.dataset.create("foo", ".")
```
<!-- end quickstart -->

See the [API Docs](https://beaker-py.readthedocs.io/en/latest/overview.html) to learn about the Beaker client's methods.
