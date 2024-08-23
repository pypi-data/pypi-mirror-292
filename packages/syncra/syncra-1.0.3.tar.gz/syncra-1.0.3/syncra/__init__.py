"""
Module for providing optional asynchronous behavior to method calls.

This module includes utilities to create methods that can be called both synchronously and asynchronously.
It provides a factory function and a decorator to facilitate this behavior.

Functions:
    sync_async_factory: Creates a callable object that can be used both synchronously and asynchronously.
    sync_compat: A decorator to make a method optionally awaitable, supporting both instance and class methods.
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


"""
Module for providing optional asynchronous behavior to method calls.

This module includes utilities to create methods that can be called both synchronously and asynchronously.
It provides a factory function and a decorator to facilitate this behavior.

Functions:
    sync_async_factory: Creates a callable object that can be used both synchronously and asynchronously.
    sync_compat: A decorator to make a method optionally awaitable, supporting both instance and class methods.
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


def wrap_classmethod_sync(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        return func(cls, *args, **kwargs)

    return wrapper


def wrap_classmethod_async(func):
    @wraps(func)
    async def wrapper(cls, *args, **kwargs):
        return await func(cls, *args, **kwargs)

    return wrapper


def sync_async_factory(sync_func: Callable[..., R], async_func: Callable[..., Awaitable[R]]) -> Callable[
    ..., Union[R, Awaitable[R]]]:
    """
    Creates a callable object that can be used both synchronously and asynchronously.
    Supports instance methods, class methods, and static methods.
    """

    @wraps(sync_func)
    def wrapper(cls_or_self: Any, *args: Any, **kwargs: Any) -> Union[R, Awaitable[R]]:
        if is_running_in_async():
            return async_func(cls_or_self, *args, **kwargs)
        else:
            return sync_func(cls_or_self, *args, **kwargs)

    return wrapper


def is_classmethod(func: Callable) -> bool:
    """
    Helper function to determine if a function is a classmethod.

    Args:
        func (Callable): The function to check.

    Returns:
        bool: True if the function is a classmethod, False otherwise.
    """
    return hasattr(func, '__self__') and isinstance(func.__self__, type)


def sync_compat(func: Callable[..., Awaitable[R]]) -> Callable[..., Union[R, Awaitable[R]]]:
    """
    A decorator to make a method optionally awaitable, supporting both instance and class methods.

    This decorator allows a method to be called both synchronously and asynchronously.

    Args:
        func (Callable[..., Awaitable[R]]): The function to decorate.

    Returns:
        Callable[..., Union[R, Awaitable[R]]]: The decorated function.
    """

    if is_classmethod(func):
        @wraps(func)
        def classmethod_wrapper(cls: Any, *args: Any, **kwargs: Any) -> Union[Any, Awaitable[Any]]:
            if not is_running_in_async():
                return asyncio.run(func(cls, *args, **kwargs))
            else:
                return asyncio.create_task(func(cls, *args, **kwargs))

        return classmethod_wrapper

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Any, Awaitable[Any]]:
        if not is_running_in_async():
            return asyncio.run(func(*args, **kwargs))
        else:
            return asyncio.create_task(func(*args, **kwargs))

    return wrapper


__all__ = ["sync_async_factory", "sync_compat", "AsyncObj", "is_running_in_async"]


def is_classmethod(func: Callable) -> bool:
    """
    Helper function to determine if a function is a classmethod.

    Args:
        func (Callable): The function to check.

    Returns:
        bool: True if the function is a classmethod, False otherwise.
    """
    return hasattr(func, '__self__') and isinstance(func.__self__, type)


def sync_compat(func: Callable[..., Awaitable[R]]) -> Callable[..., Union[R, Awaitable[R]]]:
    """
    A decorator to make a method optionally awaitable, supporting both instance and class methods.

    This decorator allows a method to be called both synchronously and asynchronously.

    Args:
        func (Callable[..., Awaitable[R]]): The function to decorate.

    Returns:
        Callable[..., Union[R, Awaitable[R]]]: The decorated function.
    """

    if is_classmethod(func):
        @wraps(func)
        def classmethod_wrapper(cls: Any, *args: Any, **kwargs: Any) -> Union[Any, Awaitable[Any]]:
            if not is_running_in_async():
                return asyncio.run(func(cls, *args, **kwargs))
            else:
                return asyncio.create_task(func(cls, *args, **kwargs))

        return classmethod_wrapper

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Any, Awaitable[Any]]:
        if not is_running_in_async():
            return asyncio.run(func(*args, **kwargs))
        else:
            return asyncio.create_task(func(*args, **kwargs))

    return wrapper


__all__ = ["sync_async_factory", "sync_compat", "AsyncObj", "is_running_in_async"]
