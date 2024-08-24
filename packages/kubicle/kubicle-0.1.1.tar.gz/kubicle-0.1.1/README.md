# Kubicle

Python background jobs on Kubernetes

No runtime dependencies, simply run Python functions on Kubernetes and get the results back.

## Installation

```
pip install kubicle
```

## Usage

Define a python function with inputs and an output that use [pydantic](https://docs.pydantic.dev/latest/) `BaseModel`

```py
from pydantic import BaseModel

class Foo(BaseModel):
    a: int
    b: str

class Bar(BaseModel):
    c: float
    d: bool


def call_me_remote(foo: Foo) -> Bar:
    ...

```

Run as a Kubernetes job

```py
from kubicle import Runner

runner = Runner()

job = runner.run(call_me_remote, Foo(a=1, b="hello"))

```

Wait for the job to finish

```py
from kubicle import JobStatus

while True:
    job.refresh()
    if job.status == JobStatus.FINISHED:
        break
```

Get the result

```py
result = job.result
bar = Bar.model_validate_json(result)
```

## Backends

Job storage can be backed by:

- Sqlite
- Postgresql

Sqlite will be used by default. To use postgres simply configure the env vars:

```sh
DB_TYPE=postgres
DB_NAME=jobs
DB_HOST=localhost
DB_USER=postgres
DB_PASS=abc123
```
