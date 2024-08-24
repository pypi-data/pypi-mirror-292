from .types import (
    FunctionCallsStore,
    MockingFunction,
    MockingValue,
)
from _pytest.monkeypatch import (
    MonkeyPatch,
)
from collections.abc import (
    Iterator,
)
import pytest as _pytest


class CustomFixturesPlugin:
    """
    A custom pytest plugin for adding general purpose fixtures
    for testing.
    """

    @_pytest.fixture(scope="session")
    def monkeysession(self) -> Iterator[MonkeyPatch]:
        """
        Session-scoped version of monkeypatch.
        """
        mpatch = MonkeyPatch()
        yield mpatch
        mpatch.undo()

    @_pytest.fixture(scope="function")
    def mocking(self, monkeypatch: MonkeyPatch) -> MockingFunction:
        store = FunctionCallsStore()

        def _mock(
            module: object, method: str, result: object
        ) -> FunctionCallsStore:
            def _mocked(*args: tuple, **kwargs: dict) -> object:
                store.append_call(args, kwargs, result)
                return result

            monkeypatch.setattr(module, method, _mocked)
            return store

        return _mock

    @_pytest.fixture(scope="function")
    def value_mocking(self, monkeypatch: MonkeyPatch) -> MockingValue:
        def _mock(module: object, method: str, result: object) -> None:
            monkeypatch.setattr(module, method, result)

        return _mock

    @_pytest.fixture(scope="function")
    def async_mocking(
        self, monkeypatch: MonkeyPatch
    ) -> Iterator[MockingFunction]:
        store = FunctionCallsStore()

        def _mock(
            module: object, method: str, result: object
        ) -> FunctionCallsStore:
            async def _mocked(*args: tuple, **kwargs: dict) -> object:
                store.append_call(args, kwargs, result)
                return result

            monkeypatch.setattr(module, method, _mocked)
            return store

        yield _mock
