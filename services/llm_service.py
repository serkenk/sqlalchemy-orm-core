from typing import Any

from config import settings


class LLMService:
    """Asynchronous wrapper service for LLM completion operations."""

    def __init__(
        self,
        client: Any | None = None,
        model: str | None = None,
    ) -> None:
        self._client = client
        self.model = model or settings.OPENAI_MODEL

    @property
    def client(self) -> Any:
        """Returns injected client or lazily initializes AsyncOpenAI client."""
        if self._client is None:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    async def generate_completion(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI backend assistant.",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Sends an asynchronous chat completion
        request to the configured LLM endpoint."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content: str | None = response.choices[0].message.content
        return content if content is not None else ""
