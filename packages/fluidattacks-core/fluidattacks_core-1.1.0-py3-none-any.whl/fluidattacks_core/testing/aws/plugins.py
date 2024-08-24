# pylint: disable=import-error
from _pytest.monkeypatch import (
    MonkeyPatch,
)
import aioboto3 as _aioboto3
from aiobotocore.config import (
    AioConfig,
)
import boto3 as _boto3
from contextlib import (
    AbstractContextManager,
    contextmanager,
)
from fluidattacks_core.testing.aws.utils import (
    mock_aio_aws,
)
from fluidattacks_core.testing.fakers import (
    initialize_db,
)
from fluidattacks_core.testing.types import (
    AsyncGeneratorFixture,
    DynamoDBResource,
    DynamoDBTable,
    FunctionFixture,
    GeneratorFixture,
    SetupFixture,
)
import moto as _moto
import os as _os
import pytest as _pytest
import pytest_asyncio as _pytest_asyncio


class MotoPlugin:
    """
    A custom pytest plugin for implementing moto easily and some services
    by default.

    Add to the plugins list on _pytest.main method.

    Mocked services enabled:
    - DynamoDB (boto3)
    - DynamoDB (aioboto3)
    """

    @_pytest.fixture(autouse=True)
    def _aws_credentials(self) -> SetupFixture:
        """
        Mocked AWS Credentials for moto.

        Autouse is enabled to ensure testing environment by default.
        """
        _os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        _os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        _os.environ["AWS_SECURITY_TOKEN"] = "testing"
        _os.environ["AWS_SESSION_TOKEN"] = "testing"
        _os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    @_pytest.fixture(scope="session")
    def _moto_session(self) -> GeneratorFixture[None]:
        """
        Starts the moto server and mocks the boto3 requests and responses.
        """
        with _moto.mock_aws():
            yield

    @_pytest.fixture(scope="session")
    def dynamodb_resource(
        self, _moto_session: GeneratorFixture[None]
    ) -> GeneratorFixture[DynamoDBResource]:
        """
        Returns a DynamoDB service resource.

        The default table is loaded for testing purposes.
        """
        session = _boto3.Session()
        resource = session.resource(service_name="dynamodb")
        initialize_db(resource)
        yield resource

    @_pytest_asyncio.fixture(scope="session")
    async def async_dynamodb_resource(
        self,
        _moto_session: GeneratorFixture[None],
        monkeysession: MonkeyPatch,
    ) -> AsyncGeneratorFixture[DynamoDBResource]:
        """
        Returns an async DynamoDB service resource (from aioboto3).

        The default table is loaded for testing purposes.
        """
        session = _aioboto3.Session()
        config = AioConfig(
            connect_timeout=10,
            max_pool_connections=0,
            read_timeout=5,
            retries={"max_attempts": 10, "mode": "standard"},
        )
        with mock_aio_aws(monkeysession):
            async with session.resource(
                service_name="dynamodb",
                config=config,
            ) as resource:
                await initialize_db(resource)
                yield resource

    @_pytest.fixture(scope="session")
    def patch_table(
        self,
        dynamodb_resource: DynamoDBResource,
        monkeysession: MonkeyPatch,
    ) -> FunctionFixture[AbstractContextManager[DynamoDBTable]]:
        """
        Context manager for patching a DynamoDB table resource variable with a
        mocked table name that you provide.

        ```
        Usage:
            with patch_table(
                dynamodb_resource, "TABLE_RESOURCE", "integrates_vms"
            ) as table:
                # Now `table` is the mocked table resource.
                yield
        ```
        """

        @contextmanager
        def _mock_table(
            module: object, resource: str, table_name: str
        ) -> GeneratorFixture[DynamoDBTable]:
            table = dynamodb_resource.Table(table_name)
            monkeysession.setattr(module, resource, table)
            yield table

        return _mock_table
