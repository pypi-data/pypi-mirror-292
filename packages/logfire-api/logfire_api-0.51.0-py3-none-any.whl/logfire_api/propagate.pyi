from typing import Any, Iterator, Mapping

__all__ = ['get_context', 'attach_context', 'ContextCarrier']

ContextCarrier = Mapping[str, Any]

def get_context() -> ContextCarrier:
    """Create a new empty carrier dict and inject context into it.

    Returns:
        A new dict with the context injected into it.

    Usage:

    ```py
    from logfire.propagate import get_context, attach_context

    logfire_context = get_context()

    ...

    # later on in another thread, process or service
    with attach_context(logfire_context):
        ...
    ```

    You could also inject context into an existing mapping like headers with:

    ```py
    from logfire.propagate import get_context

    existing_headers = {'X-Foobar': 'baz'}
    existing_headers.update(get_context())
    ...
    ```
    """
def attach_context(carrier: ContextCarrier) -> Iterator[None]:
    """Attach a context as generated by [`get_context`][logfire.propagate.get_context] to the current execution context.

    Since `attach_context` is a context manager, it restores the previous context when exiting.
    """
