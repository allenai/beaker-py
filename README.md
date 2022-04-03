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

Set the environment variable `BEAKER_TOKEN` to your Beaker [user token](https://beaker.org/user).
Then you can instantiate the Beaker client with `.from_env()`:

```python
from beaker import Beaker

beaker = Beaker.from_env(default_workspace="my_org/my_workspace")
```
<!-- end quickstart -->

See the [API Docs](https://beaker-py.readthedocs.io/en/latest/overview.html) to learn about the Beaker client's methods.
