"""
Tool call limiter — enforces max N calls per tool per agent request.
Single responsibility: decorate tools with per-invocation call counting.
"""

import threading
import functools

from config import MAX_TOOL_CALLS

# Thread-local storage for per-request call counts
_call_counts = threading.local()


def reset_call_counts():
    """Reset all tool call counters. Call this at the start of each agent request."""
    _call_counts.counts = {}


def get_call_count(tool_name: str) -> int:
    """Get current call count for a tool."""
    if not hasattr(_call_counts, "counts"):
        _call_counts.counts = {}
    return _call_counts.counts.get(tool_name, 0)


def _increment_call_count(tool_name: str) -> int:
    """Increment and return the new call count for a tool."""
    if not hasattr(_call_counts, "counts"):
        _call_counts.counts = {}
    current = _call_counts.counts.get(tool_name, 0) + 1
    _call_counts.counts[tool_name] = current
    return current


def max_calls(limit: int = MAX_TOOL_CALLS):
    """Decorator that enforces a maximum number of calls per tool per request.

    Usage:
        @max_calls(5)
        def my_tool(query: str) -> str:
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tool_name = func.__name__
            count = _increment_call_count(tool_name)
            if count > limit:
                return {
                    "error": f"Tool '{tool_name}' has reached its maximum of "
                    f"{limit} calls for this request. "
                    f"Current call count: {count}."
                }
            return func(*args, **kwargs)

        return wrapper

    return decorator
