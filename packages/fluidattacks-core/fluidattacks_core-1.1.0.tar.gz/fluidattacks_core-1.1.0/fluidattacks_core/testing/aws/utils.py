import aiobotocore.endpoint as _aiobotocore_endpoint
import botocore as _botocore
from collections.abc import (
    Awaitable,
    Callable,
    Iterator,
)
from contextlib import (
    contextmanager,
)
from dataclasses import (
    dataclass,
)
import pytest as _pytest
from typing import (
    Any,
    TypeVar,
)

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class _PatchedAWSReponseContent:
    """Patched version of `botocore.awsrequest.AWSResponse.content`"""

    content: bytes | Awaitable[bytes]

    def __await__(self) -> Iterator[bytes]:
        async def _generate_async() -> bytes:
            if isinstance(self.content, Awaitable):
                return await self.content
            return self.content

        return _generate_async().__await__()

    def decode(self, encoding: str) -> str:
        assert isinstance(self.content, bytes)
        return self.content.decode(encoding)


class PatchedAWSResponse:
    # pylint: disable=too-few-public-methods
    """Patched version of `botocore.awsrequest.AWSResponse`"""

    def __init__(self, response: Any) -> None:
        self._response = response
        self.status_code = response.status_code
        self.headers = response.headers
        self.url = response.url
        self.content = _PatchedAWSReponseContent(response.content)
        self.raw = response.raw
        if not hasattr(self.raw, "raw_headers"):
            self.raw.raw_headers = {}


class PatchedRetryContext(_botocore.retries.standard.RetryContext):
    """Patched version of `botocore.retries.standard.RetryContext`"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if kwargs.get("http_response"):
            kwargs["http_response"] = PatchedAWSResponse(
                kwargs["http_response"]
            )
        super().__init__(*args, **kwargs)


def _factory(
    original: Callable[[Any, T], Awaitable[R]],
) -> Callable[[Any, T], Awaitable[R]]:
    async def patched_convert_to_response_dict(
        http_response: _botocore.awsrequest.AWSResponse, operation_model: T
    ) -> R:
        return await original(
            PatchedAWSResponse(http_response),
            operation_model,
        )

    return patched_convert_to_response_dict


@contextmanager
def mock_aio_aws(
    monkeypatch: _pytest.MonkeyPatch,
) -> Iterator[None]:
    """
    (Context manager)
    Patches boto3 and aioboto3 using monkeypatch for testing purposes.

    Inspired by a GitHub discussion
    (https://github.com/aio-libs/aiobotocore/issues/755).
    """
    monkeypatch.setattr(
        _aiobotocore_endpoint,
        "convert_to_response_dict",
        _factory(_aiobotocore_endpoint.convert_to_response_dict),
    )
    monkeypatch.setattr(
        _botocore.retries.standard, "RetryContext", PatchedRetryContext
    )
    yield
