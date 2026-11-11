from unittest.mock import AsyncMock, MagicMock

import pytest

from services.llm_service import LLMService


@pytest.mark.asyncio
async def test_generate_completion_success() -> None:
    """Verifies that LLMService accurately extracts and returns message content."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Test AI generated response"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = mock_response

    llm_service = LLMService(client=mock_client, model="llama3.2:1b")
    result = await llm_service.generate_completion(
        prompt="Explain FastAPI",
        system_prompt="You are an engineering mentor.",
    )

    assert result == "Test AI generated response"
    mock_client.chat.completions.create.assert_awaited_once_with(
        model="llama3.2:1b",
        messages=[
            {"role": "system", "content": "You are an engineering mentor."},
            {"role": "user", "content": "Explain FastAPI"},
        ],
        temperature=0.7,
        max_tokens=500,
    )


@pytest.mark.asyncio
async def test_llm_service_ollama_default_config() -> None:
    """
    Verifies that LLMService configures
    local Ollama endpoints correctly by default.
    """
    service = LLMService()
    assert service.model == "qwen2.5-coder:1.5b"
    assert service.base_url == "http://localhost:11434/v1"
