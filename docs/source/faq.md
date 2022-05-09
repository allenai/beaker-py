# FAQ

```{rubric} Do I need to install the Beaker [command-line client](https://github.com/allenai/beaker) for beaker-py to work?
```

> No, **beaker-py** is written in pure Python. It communicates with the Beaker server directly through HTTP requests, so you don't need to have the command-line client installed.

```{rubric} Do I need Docker?
```

> Not necessarily. **beaker-py** will work fine without Docker, unless you want to do something that requires Docker, like uploading an image to Beaker ({meth}`Beaker.image.create <beaker.services.ImageClient.create>`).

```{rubric} Is there way to suppress the progress bars that certain methods print out?
```

> Yes, just pass the `quiet=True` parameter to those methods.

```{rubric} I keep getting warnings that I should upgrade beaker-py, but I don't want to. Can I turn those warnings off?
```

> Yes, just pass `check_for_upgrades=False` to {class}`~beaker.Beaker()` or {meth}`Beaker.from_env() <beaker.Beaker.from_env>`.

```{rubric} What's the different between a task and a job?
```

> In Beaker, tasks are the fundamental unit of work. A {class}`~beaker.data_model.job.Job` is just an execution of a task. So a {class}`~beaker.data_model.experiment.Task` can have any number of {data}`~beaker.data_model.experiment.Task.jobs` associated with it, but a job is always associated with at most a single task (only "session" type jobs won't be associated with a task).
