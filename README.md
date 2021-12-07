# beaker-py

A [Beaker](https://beaker.org) client for Python.

## Quick links

- [Documentation](https://beaker-py.readthedocs.io/)
- [PyPI Package](https://pypi.org/project/beaker-py/)
- [Contributing](https://github.com/allenai/beaker-py/blob/main/CONTRIBUTING.md)
- [License](https://github.com/allenai/beaker-py/blob/main/LICENSE)

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

Create a Beaker client with your Beaker [user token](https://beaker.org/user):

```python
from beaker import Beaker, Config

beaker = Beaker(Config(user_token="my beaker token", default_workspace="my_org/my_workspace"))
```

You can also create your client from a beaker config file or environment variables with:

```python
beaker = Beaker.from_env()
```

<!-- end quickstart -->
