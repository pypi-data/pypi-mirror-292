import contextvars
from functools import cached_property
from typing import Any, TypeVar

weba_context: contextvars.ContextVar[Any] = contextvars.ContextVar("current_weba_context")

T = TypeVar("T")


class Context:
    @cached_property
    def context(self):
        context = weba_context.get(None)

        if not context:
            self._weba_context_token = weba_context.set(self)
            context = self

        return context

    async def __aenter__(self):
        return self.context

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        weba_context.reset(self._weba_context_token)
