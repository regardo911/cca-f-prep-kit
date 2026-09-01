"""Resilience layer — Appendix A, from Chapter 5.

Exponential-backoff retry with a circuit breaker, covering the three transient
failure modes the exam grades: upstream refusal, MCP tool failure, and
rate-limit / overload. Drops around any Claude API or tool call.

Two classes ship here, and you want the second one.

`FallbackWrapper` is the appendix listing, byte for byte. Its `__call__` is
`async` and does `await call()`, but every call site the book gives you is a
synchronous client — `client = anthropic.Anthropic()` at ch05:24, ch05:106,
ch05:138 and ch08:49, wrapped as `await with_fallback(lambda:
client.messages.create(...))` at ch05:187. Awaiting the non-awaitable return of
a sync SDK call raises `TypeError: object Message can't be used in 'await'
expression`. Keeping the listing here means you can hold the book open beside
it and see exactly what you are comparing against.

`SyncFallbackWrapper` is the same architecture with `time.sleep` instead of
`asyncio.sleep`, and it is the one that works with the book's own call sites.
Same three attempts, same 1s/2s/4s backoff, same circuit threshold of ten. We
went synchronous rather than switching the book to `anthropic.AsyncAnthropic()`
because that would have meant rewriting every printed call site in five
chapters; this way the only thing that changes is which wrapper you import.

Needs your own ANTHROPIC_API_KEY when you point it at a real call. It is a
library, not a program: there is nothing to run standalone.
"""

# fallback_wrapper.py
import asyncio
import logging
import anthropic

logger = logging.getLogger(__name__)

class CircuitOpen(Exception):
    """Raised when the circuit breaker has tripped."""

class FallbackWrapper:
    def __init__(self, max_attempts=3, base_delay=1.0, circuit_threshold=10):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.circuit_threshold = circuit_threshold
        self._consecutive_failures = 0

    async def __call__(self, call):
        if self._consecutive_failures >= self.circuit_threshold:
            raise CircuitOpen(
                f"Circuit open after {self._consecutive_failures} consecutive failures"
            )
        last_exc = None
        for attempt in range(self.max_attempts):
            try:
                result = await call()
                self._consecutive_failures = 0
                return result
            except (anthropic.RateLimitError, anthropic.APITimeoutError) as exc:
                last_exc = exc
                logger.warning("retryable failure attempt=%d: %r", attempt, exc)
                await asyncio.sleep(self.base_delay * (2 ** attempt))
        self._consecutive_failures += 1
        raise last_exc


import time  # noqa: E402 — kept out of the block above so it stays the book's


class SyncFallbackWrapper:
    """The corrected wrapper. Same architecture, synchronous call sites.

    Use it exactly the way ch05:187 tells you to, minus the await:

        retry = SyncFallbackWrapper()
        message = retry(lambda: client.messages.create(...))
    """

    def __init__(self, max_attempts=3, base_delay=1.0, circuit_threshold=10):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.circuit_threshold = circuit_threshold
        self._consecutive_failures = 0

    def __call__(self, call):
        if self._consecutive_failures >= self.circuit_threshold:
            raise CircuitOpen(
                f"Circuit open after {self._consecutive_failures} consecutive failures"
            )
        last_exc = None
        for attempt in range(self.max_attempts):
            try:
                result = call()
                self._consecutive_failures = 0
                return result
            except (anthropic.RateLimitError, anthropic.APITimeoutError) as exc:
                last_exc = exc
                logger.warning("retryable failure attempt=%d: %r", attempt, exc)
                time.sleep(self.base_delay * (2 ** attempt))
        self._consecutive_failures += 1
        raise last_exc
