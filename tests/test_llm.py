from unittest.mock import AsyncMock, MagicMock

import pytest

from services.llm_service import LLMService


@pytest.mark.asyncio
async def test_generate_completion_success() -> None:
    """Verifies that LLMService accurately extracts and returns message content."""
    # 1. Construct Mock OpenAI API Response Structure
    mock_choice = MagicMock()
    mock_choice.message.content = "Test AI generated response"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    # 2. Mock AsyncOpenAI Client structure
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = mock_response

    # 3. Instantiate LLMService with Injected Mock Client
    llm_service = LLMService(client=mock_client, model="gpt-4o-mini")
    result = await llm_service.generate_completion(
        prompt="Explain FastAPI",
        system_prompt="You are an engineering mentor.",
    )

    # 4. Assertions
    assert result == "Test AI generated response"
    mock_client.chat.completions.create.assert_awaited_once_with(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an engineering mentor."},
            {"role": "user", "content": "Explain FastAPI"},
        ],
        temperature=0.7,
        max_tokens=500,
    )
