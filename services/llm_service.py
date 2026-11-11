from typing import Any

from config import settings


class LLMService:
    """Asynchronous wrapper service for LLM completion operations.

    Supports both remote OpenAI models and local Ollama deployments.
    """

    def __init__(
        self,
        client: Any | None = None,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._client = client
        self.model = model or settings.OLLAMA_MODEL
        self.base_url = base_url or f"{settings.OLLAMA_BASE_URL}/v1"
        self.api_key = api_key or "ollama"

    @property
    def client(self) -> Any:
        """Returns injected client or lazily initializes AsyncOpenAI client."""
        if self._client is None:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        return self._client

    async def generate_completion(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI backend assistant.",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Sends an asynchronous chat completion
        request to the configured LLM endpoint.
        """
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
