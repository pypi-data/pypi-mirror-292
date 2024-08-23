from functools import partial

import pytest
import asyncio

from syncra import sync_async_factory, sync_compat, AsyncObj, is_running_in_async


@sync_compat
async def async_function(x):
    await asyncio.sleep(0.1)
    return x * 2


def test_sync_compat_decorator_sync():
    result = async_function(5)
    assert result == 10  # Expected result for sync call


@pytest.mark.asyncio
async def test_sync_compat_decorator_async():
    result = await async_function(5)
    assert result == 10  # Expected result for async call


class MyAsyncObj(AsyncObj):
    async def __ainit__(self, x):
        self.x = x


@pytest.mark.asyncio
async def test_async_obj_initialization():
    obj = await MyAsyncObj(10)
    assert obj.x == 10
    assert obj.async_state == "[initialization done and successful]"


class MyAsyncObj(AsyncObj):
    async def __ainit__(self, x):
        self.x = x


@pytest.mark.asyncio
async def test_async_obj_initialization():
    obj = await MyAsyncObj(10)
    assert obj.x == 10
    assert obj.async_state == "[initialization done and successful]"


# Test sync_async_factory
def test_sync_async_factory_sync():
    def sync_func(x: int) -> int:
        return x * 2

    async def async_func(x: int) -> int:
        await asyncio.sleep(0.1)
        return x * 2

    sync_async = sync_async_factory(sync_func, async_func)

    # Test synchronous call
    result = sync_async(5)
    assert result == 10  # Expected result for sync_func(5)


@pytest.mark.asyncio
async def test_sync_async_factory_async():
    def sync_func(x: int) -> int:
        return x * 2

    async def async_func(x: int) -> int:
        await asyncio.sleep(0.1)
        return x * 2

    sync_async = sync_async_factory(sync_func, async_func)

    # Test asynchronous call
    result = await sync_async(5)
    assert result == 10  # Expected result for async_func(5)


# Test sync_async decorator
def test_sync_async_decorator_sync():
    @sync_compat
    async def decorated_func(x: int) -> int:
        await asyncio.sleep(0.1)
        return x * 2

    # Test synchronous call
    result = decorated_func(5)
    assert result == 10  # Expected result for decorated_func(5)


@pytest.mark.asyncio
async def test_sync_async_decorator_async():
    @sync_compat
    async def decorated_func(x: int) -> int:
        await asyncio.sleep(0.1)
        return x * 2

    # Test asynchronous call
    result = await decorated_func(5)
    assert result == 10  # Expected result for decorated_func(5)


# Test exception handling in sync_async_factory
def test_sync_async_factory_sync_exception():
    def sync_func(x: int) -> int:
        raise ValueError("Synchronous error")

    async def async_func(x: int) -> int:
        raise ValueError("Asynchronous error")

    sync_async = sync_async_factory(sync_func, async_func)

    # Test synchronous call
    try:
        sync_async(5)
    except ValueError as e:
        assert str(e) == "Synchronous error"


@pytest.mark.asyncio
async def test_sync_async_factory_async_exception():
    def sync_func(x: int) -> int:
        raise ValueError("Synchronous error")

    async def async_func(x: int) -> int:
        raise ValueError("Asynchronous error")

    sync_async = sync_async_factory(sync_func, async_func)

    # Test asynchronous call
    try:
        await sync_async(5)
    except ValueError as e:
        assert str(e) == "Asynchronous error"


# Test different return types in sync_async_factory
def test_sync_async_factory_sync_return_types():
    def sync_func(x: int) -> str:
        return str(x * 2)

    async def async_func(x: int) -> str:
        await asyncio.sleep(0.1)
        return str(x * 2)

    sync_async = sync_async_factory(sync_func, async_func)

    # Test synchronous call
    result = sync_async(5)
    assert result == "10"  # Expected result for sync_func(5)


@pytest.mark.asyncio
async def test_sync_async_factory_async_return_types():
    def sync_func(x: int) -> str:
        return str(x * 2)

    async def async_func(x: int) -> str:
        await asyncio.sleep(0.1)
        return str(x * 2)

    sync_async = sync_async_factory(sync_func, async_func)

    # Test asynchronous call
    result = await sync_async(5)
    assert result == "10"  # Expected result for async_func(5)


# Test edge cases in sync_async_factory
def test_sync_async_factory_sync_edge_cases():
    def sync_func(x: int) -> int:
        return x * 2

    async def async_func(x: int) -> int:
        await asyncio.sleep(0.1)
        return x * 2

    sync_async = sync_async_factory(sync_func, async_func)

    # Test zero
    result = sync_async(0)
    assert result == 0  # Expected result for sync_func(0)

    # Test negative number
    result = sync_async(-5)
    assert result == -10  # Expected result for sync_func(-5)

    # Test large number
    result = sync_async(10 ** 6)
    assert result == 2 * 10 ** 6  # Expected result for sync_func(10**6)


@pytest.mark.asyncio
async def test_sync_async_factory_async_edge_cases():
    def sync_func(x: int) -> int:
        return x * 2

    async def async_func(x: int) -> int:
        await asyncio.sleep(0.1)
        return x * 2

    sync_async = sync_async_factory(sync_func, async_func)

    # Test zero
    result = await sync_async(0)
    assert result == 0  # Expected result for async_func(0)

    # Test negative number
    result = await sync_async(-5)
    assert result == -10  # Expected result for async_func(-5)

    # Test large number
    result = await sync_async(10 ** 6)
    assert result == 2 * 10 ** 6  # Expected result for async_func(10**6)


@sync_compat
async def async_function_with_args(x, y, z=0):
    await asyncio.sleep(0.1)
    return x + y + z


def test_sync_compat_decorator_sync_multiple_args():
    result = async_function_with_args(5, 3, z=2)
    assert result == 10  # Expected result for sync call


@pytest.mark.asyncio
async def test_sync_compat_decorator_async_multiple_args():
    result = await async_function_with_args(5, 3, z=2)
    assert result == 10  # Expected result for async call


@sync_compat
async def combined_function(x):
    await asyncio.sleep(0.1)
    return x * 3


def sync_function(x):
    return x * 2


combined_sync_async = sync_async_factory(sync_function, combined_function)


def test_combined_sync_async_sync():
    result = combined_sync_async(5)
    assert result == 10  # Expected result for sync call


@pytest.mark.asyncio
async def test_combined_sync_async_async():
    result = await combined_sync_async(5)
    assert result == 15  # Expected result for async call


class AdvancedAsyncObj(AsyncObj):
    async def __ainit__(self, x, y):
        self.x = x
        self.y = y


@pytest.mark.asyncio
async def test_async_obj_subclass_initialization():
    obj = await AdvancedAsyncObj(10, 20)
    assert obj.x == 10
    assert obj.y == 20
    assert obj.async_state == "[initialization done and successful]"


@pytest.mark.asyncio
async def test_is_running_in_async_async_context():
    assert is_running_in_async() is True


def test_is_running_in_async_sync_context():
    assert is_running_in_async() is False


class MyClass:
    @classmethod
    def sync_class_method(cls, x):
        return x * 2

    @classmethod
    async def async_class_method(cls, x):
        await asyncio.sleep(0.1)
        return x * 2


MyClass.combined_class_method = sync_async_factory(
    lambda x: MyClass.sync_class_method(x),
    lambda x: MyClass.async_class_method(x)
)


# Test Functions
def test_class_method_sync_combined_class_methods():
    result = MyClass.combined_class_method(5)
    assert result == 10

@pytest.mark.asyncio
async def test_class_method_async_combined_class_methods():
    result = await MyClass.combined_class_method(5)
    assert result == 10