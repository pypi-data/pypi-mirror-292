import colorama
from functools import wraps
from time import perf_counter
from contextlib import contextmanager
from typing import TypeVar, Callable, Any

# custom packages
from pygfdrivers.common.util.logger_manager import LoggerManager, LOGGING_MODE

colorama.init()
color = colorama.Fore.LIGHTMAGENTA_EX
reset = colorama.Style.RESET_ALL

log = LoggerManager('code_timer', LOGGING_MODE.DEBUG).log

Func = TypeVar('Func', bound=Callable[..., Any])


@contextmanager
def time_code_block(label: str) -> None:
    start = perf_counter()
    try:
        yield
    finally:
        log.timer(f"'{label}' took {(perf_counter() - start):.5f} seconds to execute.")


@contextmanager
def custom_timer(label: str) -> None:
    start = perf_counter()
    try:
        yield
    finally:
        print(f"{color}'{label}' took {(perf_counter() - start):.5f} seconds to execute.{reset}")


def time_func_execution(func: Func) -> Func:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start = perf_counter()
        result = func(self, *args, **kwargs)
        log.timer(f"'{func.__name__}' took {(perf_counter() - start):.5f} seconds to execute.")
        return result
    return wrapper  # type: ignore
