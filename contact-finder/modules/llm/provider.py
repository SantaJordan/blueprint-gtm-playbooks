"""
LLM Provider Abstraction
Supports OpenAI and Anthropic with unified interface
"""

from abc import ABC, abstractmethod
from typing import Any
import json


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 500
    ) -> str:
        """Generate a text completion"""
        pass

    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        schema: dict | None = None,
        system: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 500
    ) -> dict:
        """Generate a JSON completion"""
        pass

    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from response, handling markdown code blocks"""
        response = response.strip()

        # Handle markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        return json.loads(response)


def get_provider(config: dict) -> LLMProvider:
    """Factory function to get the configured LLM provider

    Args:
        config: Either the full config dict (with config["llm"]) or just the llm section
    """
    # Handle both full config and llm-only config
    llm_config = config.get("llm", config) if "provider" not in config else config

    provider_name = llm_config.get("provider", "openai")

    if provider_name == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(
            api_key=llm_config.get("openai_api_key"),
            model=llm_config.get("model", "gpt-4o-mini"),
            default_temperature=llm_config.get("temperature", 0.1),
            default_max_tokens=llm_config.get("max_tokens", 500)
        )
    elif provider_name == "anthropic":
        from .anthropic_provider import AnthropicProvider
        return AnthropicProvider(
            api_key=llm_config.get("anthropic_api_key"),
            model=llm_config.get("model", "claude-3-haiku-20240307"),
            default_temperature=llm_config.get("temperature", 0.1),
            default_max_tokens=llm_config.get("max_tokens", 500)
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
