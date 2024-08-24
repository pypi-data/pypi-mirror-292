# Fluid Attacks Core Library

<p align="center">
  <img alt="logo" src="https://res.cloudinary.com/fluid-attacks/image/upload/f_auto,q_auto/v1/airs/menu/Logo?_a=AXAJYUZ0.webp" />
</p>

### Disclaimer

This library was developed for Fluid Attacks projects. That specific
context is reflected in some presets and configurations.

## Importing types

```python
from fluidattacks_core.{module}.types import (
    ...
)
```

where `{module}` is one of the following:

- authz
- testing

## Publishing a new version

1. Make any changes you want to the library.
1. Run the Python linter:
   ```bash
   m . /lintPython/dirOfModules/commonUtilsPypiFluidattackscore
   ```
1. Upgrade the library version in `pyproject.toml`.
   > Make sure to do this as it is required for your changes to be published.
1. Push your changes using the `common\` pipeline.
1. Once you reach production,
   the new version of the library should become available.

---

# Core: Testing

### Motivation

Standardize test fundamentals for current and new projects in
any organization could be a hard task.
Also, thanks to pytest malleability, we find different solutions solving
the same problems and a harder test maintainability.

Using pytest, we find that developers tend to use a lot of features
(fixtures, patches, marks, etc.) without any standard but pytest is still a
very simple and powerful tool.

For this reason, we decided to create a pytest wrapper that includes some
presets and defines testing standards for us.

### Description

This library aims to provide a simple way to write
**unit and integration tests** for Python products using boto3 and aioboto3
services mainly.

Philosophy of this package is to be simple and include the most common
testing features in a standard way.

## Table of Contents

1. [Usage](#usage)
1. [Tagging](#tagging)
1. [Fakers](#fakers)
1. [Mocking](#mocking)

## Usage

```bash
python -m fluidattacks_core.testing --help

: '
usage: fluidattacks_core.testing [-h] [--target [TARGET]] [--src [SRC]] [--test-folder [TEST_FOLDER]] [--scope SCOPE]

🏹 Python package for unit and integration testing through Fluid Attacks projects 🏹

options:
  -h, --help            show this help message and exit
  --target [TARGET]     Folder to start the tests. Default is current folder.
  --src [SRC]           The source code for coverage report. Default is src.
  --test-folder [TEST_FOLDER]
                        Folder with tests inside the target. Default is test.
  --scope SCOPE         Type and module to test.
```

`target` is the main folder where test and coverage folders will be resolved.

`src` is the folder where the source code is located (used for coverage analysis)
and by default it is `{target}/src`.

`test-folder` is the folder where tests files live. Default is `{target}/test`.

`scope`, the only required argument, is the test folder to run from
`{test-folder}/unit/src`.

An example of usage is:

```bash
python -m fluidattacks_core.testing --scope billing
```

## Tagging

You can use one or multiple tags for classifying the test methods, but tags
are required:

```python
from fluidattacks_core.testing import tag

@tag.api
@tag.billing
def test_billing() -> None:
    ...

@tag.api
@tag.auth
def test_auth() -> None:
    ...
```

Recommendations:

- Use two tags: one for the main context or module (api, resolvers, mutations,
  etc) and one for the file name that you are testing (to check by file faster).
- Don't use special pytest tags like `slow`, `skip`, `only`, `xfail`, etc.
  Errors cannot be ignored and skip, only or slow tags can be replaced using
  normal tags.

Also, you can add multiple inputs using `@tag.parametrize()` like in [pytest](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions).

## Fakers

Some fakers are available to generate stub data for tests:

- `fake_vulnerability()`.
- `fake_finding()`.
- `fake_group()`.
- `fake_stakeholder(email)`.

## AWS Services Testing

### DynamoDB

DynamoDB resource is mocked via fixtures using moto:

```python
from fluidattacks_core.testing import tag

@tag.api
@tag.billing
def test_billing(dynamodb_resource: DynamoDBResource) -> None:
    table = dynamodb_resource.Table("integrates_vms")
    ...
```

An example `integrates_vms` table is loaded on the resource creation and it
enables DynamoDB Streams also. It can be used for your tests.

For a well implemented DynamoDB mocking, you need to mock the DynamoDB resource
that the code are using. For example, if TABLE constant has the real DyanmoDB
table and it is defined on `database.resource`, you can do this:

```python
import database.resource
from fluidattacks_core.testing import tag
from fluidattacks_core.testing.types import (
    DynamoDBResource,
)

@tag.api
@tag.billing
def test_billing(dynamodb_resource: DynamoDBResource) -> None:
    table = dynamodb_resource.Table("integrates_vms")
    value_mocking(database.resource, "TABLE", table)
    ...
```

With this, your application will use mocked DynamoDB service instead of asking
for a real one. You can add the testing data after that using fakers.

## AWS Async Services Testing

### DynamoDB

aioboto3 is slightly different than boto3 to test. Resource changes
and every request must be awaited:

```python
import database.resource
from fluidattacks_core.testing import tag
from fluidattacks_core.testing.types import (
    FunctionFixture,
    MockingValue,
)
from typing import Any

@tag.asyncio
@tag.api
@tag.billing
def test_billing(
  async_dynamodb_resource: Any,
  value_mocking: FunctionFixture[MockingValue]
) -> None:
    table = await async_dynamodb_resource.Table("integrates_vms")
    value_mocking(database.resource, "TABLE", table)

    await table.put_item(Item=fake_vulnerability())
    ...
```

**Note:** It's required to add a session-scoped event_loop fixture
for running properly this mock. Include this snippet on your conftest file:

```python
from fluidattacks_core.testing import injectable
import asyncio
from typing import (
    Iterator,
)

@injectable(scope="session")
def event_loop() -> Iterator:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

```

## Mocking

Some utilities are available via dependency injection to test methods.
Mocking is one of them and it allows you to change the behavior and returns of
any method or class in your code.

You get an excellent mocking if you use it **in external dependencies only**
to ensure that the tests are isolated and don't affect the real behavior of the
code. Think that if you mock any function or value in the code, you could hide
unexpected behaviors and errors.

### Functions

You can mock functions using `mocking`:

```python
from fluidattacks_core.testing import tag
from fluidattacks_core.testing.types import MockingFunction

import requests

@tag.billing
def test_billing(mocking: MockingFunction) -> None:
    mock_post = mocking(requests, "post", { "status_code": 200 })

    ...

    call_list = mock_post.calls()
    assert len(call_list) == 1
```

It changes the behavior of the `post` method from the `requests` module to
return always `{ "status_code": 200 }`. The `mock_post` object stores every call
running the tests to the method for assertion purposes.

Check the `.calls()` method for more information.

### Values

Mock values using `value_mocking`:

```python
import database.resource
from fluidattacks_core.testing import tag
from fluidattacks_core.testing.types import (
    FunctionFixture,
    MockingValue,
)
from typing import Any

@tag.api
@tag.billing
def test_billing(
  async_dynamodb_resource: Any,
  value_mocking: FunctionFixture[MockingValue]
) -> None:
    table = await async_dynamodb_resource.Table("integrates_vms")
    value_mocking(database.resource, "TABLE", table)

    # TABLE will act as table variable
    ...
```

---

More instructions coming soon...
