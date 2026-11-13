"""Provider adapters. Each module exposes ``async def generate(prompt, model)``."""


class ProviderError(Exception):
    """The upstream model failed. Callers must not charge a limit for this."""
