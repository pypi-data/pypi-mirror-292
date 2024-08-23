"""
Module for providing optional asynchronous behavior to method calls.

This module includes utilities to create methods that can be called both synchronously and asynchronously.
It provides a factory function and a decorator to facilitate this behavior.

Functions:
    sync_async_factory: Creates a callable object that can be used both synchronously and asynchronously.
    sync_async: A decorator to make a method optionally awaitable.
"""

import traceback
from typing import Callable, Any, TypeVar, Awaitable, Union
import asyncio
from functools import wraps

R = TypeVar('R')


def is_running_in_async():
    try:
        loop = asyncio.get_running_loop()
        return loop.is_running()
    except RuntimeError:
        return False


class AsyncObj:
    def __init__(self, *args, **kwargs):
        """
        Standard constructor used for arguments pass
        Do not override. Use __ainit__ instead
        """
        self.__storedargs = args, kwargs
        self.async_initialized = False

    async def __ainit__(self, *args, **kwargs):
        """ Async constructor, you should implement this """

    async def __initobj(self):
        """ Crutch used for __await__ after spawning """
        assert not self.async_initialized
        self.async_initialized = True
        await self.__ainit__(*self.__storedargs[0],
                             **self.__storedargs[1])  # pass the parameters to __ainit__ that passed to __init__
        return self

    def __await__(self):
        return self.__initobj().__await__()

    def __init_subclass__(cls, **kwargs):
        assert asyncio.iscoroutinefunction(cls.__ainit__), \
            f"{cls.__name__}.__ainit__ must be an async function"

    @property
    def async_state(self):
        if not self.async_initialized:
            return "[initialization pending]"
        return "[initialization done and successful]"


def sync_async_factory(sync_func: Callable[..., R], async_func: Callable[..., Awaitable[R]]) -> Callable[
    ..., Union[R, Awaitable[R]]]:
    """
    Creates a callable object that can be used both synchronously and asynchronously.

    Args:
        sync_func (Callable[..., R]): The synchronous function to call.
        async_func (Callable[..., Awaitable[R]]): The asynchronous function to call.

    Returns:
        Callable[..., Union[R, Awaitable[R]]]: A callable object that can be used both synchronously and asynchronously.
    """

    class SyncAsync:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """
            Initialize the SyncAsync instance.

            Args:
                *args (Any): Positional arguments to pass to the functions.
                **kwargs (Any): Keyword arguments to pass to the functions.
            """
            self.args = args
            self.kwargs = kwargs

        def __call__(self, *args: Any, **kwargs: Any) -> R:
            """
            Synchronous call handler.

            Args:
                *args (Any): Positional arguments to pass to the synchronous function.
                **kwargs (Any): Keyword arguments to pass to the synchronous function.

            Returns:
                R: The result of the synchronous function call.
            """
            if args or kwargs:
                return sync_func(*args, **kwargs)
            else:
                return sync_func(*self.args, **self.kwargs)

        def __await__(self) -> Any:
            """
            Asynchronous call handler.

            Returns:
                Any: The result of the asynchronous function call.
            """
            return (yield from async_func(*self.args, **self.kwargs).__await__())

    def wrapper(*args: Any, **kwargs: Any) -> Union[R, Awaitable[R]]:
        """
        Wrapper function to determine the context (sync or async) and return the appropriate result.

        Args:
            *args (Any): Positional arguments to pass to the functions.
            **kwargs (Any): Keyword arguments to pass to the functions.

        Returns:
            Union[R, Awaitable[R]]: The result of the synchronous or asynchronous function call.
        """
        if is_running_in_async():
            return SyncAsync(*args, **kwargs)
        else:
            return sync_func(*args, **kwargs)

    return wrapper


def sync_compat(func: Callable[..., Awaitable[R]]) -> Callable[..., Union[R, Awaitable[R]]]:
    """
    A decorator to make a method optionally awaitable.

    This decorator allows a method to be called both synchronously and asynchronously.

    Args:
        func (Callable[..., Awaitable[R]]): The function to decorate.

    Returns:
        Callable[..., Union[R, Awaitable[R]]]: The decorated function.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Any, Awaitable[Any]]:
        if not is_running_in_async():
            return asyncio.run(func(*args, **kwargs))

        else:
            return asyncio.create_task(func(*args, **kwargs))

    return wrapper


__all__ = ["sync_async_factory", "sync_compat", "AsyncObj", "is_running_in_async"]
