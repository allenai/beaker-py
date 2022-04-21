# FAQ

```{rubric} Do I need to install the Beaker [command-line client](https://github.com/allenai/beaker) for beaker-py to work?
```

> No, **beaker-py** is written in pure Python. It communicates with the Beaker server directly through HTTP requests,
so you don't need to have the command-line client installed.

```{rubric} Do I need Docker?
```

> Not necessarily. **beaker-py** will work fine without Docker, unless you want to do something that requires Docker,
like uploading an image to Beaker ({meth}`Beaker.image.create <beaker.services.ImageClient.create>`).

```{rubric} Is there way to suppress the progress bars that certain methods print out?
```

> Yes, just pass the `quiet=True` parameter to those methods.
