"""
OpenRouter client wrapper for parallel API calls.

Uses OpenRouter's OpenAI-compatible API to run Claude models
as a parallel provider alongside direct Anthropic calls.
This helps avoid rate limits by splitting load across providers.
"""

import httpx
import asyncio
from typing import Optional, List, Dict, Any


class OpenRouterClient:
    """OpenRouter API client with OpenAI-compatible interface."""

    BASE_URL = "https://openrouter.ai/api/v1"

    # Model mapping: Anthropic model IDs -> OpenRouter model IDs
    MODEL_MAP = {
        "claude-sonnet-4-5-20250929": "anthropic/claude-sonnet-4.5",
        "claude-haiku-4-5-20251001": "anthropic/claude-haiku-4.5",
        "claude-opus-4-5-20251101": "anthropic/claude-opus-4.5",
        "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4",
    }

    def __init__(self, api_key: str, site_url: str = "https://blueprint-gtm.ai", app_name: str = "Blueprint GTM Worker"):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key (sk-or-v1-...)
            site_url: Your site URL for OpenRouter tracking
            app_name: Your app name for OpenRouter tracking
        """
        self.api_key = api_key
        self.site_url = site_url
        self.app_name = app_name
        self.client = httpx.AsyncClient(timeout=120.0)

    def _map_model(self, anthropic_model: str) -> str:
        """Map Anthropic model ID to OpenRouter model ID."""
        return self.MODEL_MAP.get(anthropic_model, f"anthropic/{anthropic_model}")

    async def create_message(
        self,
        model: str,
        max_tokens: int,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using OpenRouter.

        Args:
            model: Anthropic model ID (will be mapped to OpenRouter format)
            max_tokens: Maximum tokens in response
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt

        Returns:
            OpenRouter response in Anthropic-like format
        """
        openrouter_model = self._map_model(model)

        # Build request
        payload = {
            "model": openrouter_model,
            "max_tokens": max_tokens,
            "messages": messages,
        }

        if system:
            # OpenRouter uses system as first message or dedicated field
            payload["messages"] = [{"role": "system", "content": system}] + messages

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
            "Content-Type": "application/json",
        }

        response = await self.client.post(
            f"{self.BASE_URL}/chat/completions",
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            error_text = response.text
            raise Exception(f"OpenRouter API error {response.status_code}: {error_text}")

        data = response.json()

        # Convert OpenRouter response to Anthropic-like format
        return OpenRouterResponse(data)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class OpenRouterResponse:
    """Wrapper to make OpenRouter response look like Anthropic response."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self.content = [OpenRouterContent(data)]
        self.usage = data.get("usage", {})
        self.model = data.get("model", "")


class OpenRouterContent:
    """Wrapper for message content."""

    def __init__(self, data: Dict[str, Any]):
        choices = data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            self.text = message.get("content", "")
        else:
            self.text = ""


class DualClaudeMessages:
    """Messages interface for DualClaudeClient - matches anthropic.messages interface."""

    def __init__(self, dual_client: 'DualClaudeClient'):
        self._client = dual_client

    async def create(
        self,
        model: str,
        max_tokens: int,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        **kwargs
    ):
        """Create a message using either Anthropic or OpenRouter."""
        return await self._client._create_message(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            system=system,
            **kwargs
        )


class DualClaudeClient:
    """
    Dual-provider Claude client that alternates between Anthropic and OpenRouter.

    This helps avoid rate limits by splitting API calls across providers.
    Provides same interface as AsyncAnthropic (client.messages.create()).

    Note: Extended thinking is only supported via Anthropic API (not OpenRouter).
    Use _force_anthropic() when extended thinking is required.
    """

    def __init__(self, anthropic_client, openrouter_key: Optional[str] = None):
        """
        Initialize dual client.

        Args:
            anthropic_client: AsyncAnthropic client instance
            openrouter_key: Optional OpenRouter API key (if None, only uses Anthropic)
        """
        self.anthropic = anthropic_client
        self.openrouter = OpenRouterClient(openrouter_key) if openrouter_key else None
        self._call_count = 0
        self._use_openrouter = False
        # Expose messages interface like AsyncAnthropic
        self.messages = DualClaudeMessages(self)

    async def _create_message(
        self,
        model: str,
        max_tokens: int,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        **kwargs
    ):
        """
        Create a message using either Anthropic or OpenRouter.

        Args:
            model: Model ID
            max_tokens: Max tokens
            messages: Message list
            system: System prompt

        Returns:
            Claude response (from either provider)
        """
        # Decide which provider to use (round-robin)
        use_or = self.openrouter and self._use_openrouter

        # Toggle for next call
        self._use_openrouter = not self._use_openrouter
        self._call_count += 1

        if use_or:
            try:
                print(f"[DualClient] Using OpenRouter (call #{self._call_count})")
                return await self.openrouter.create_message(
                    model=model,
                    max_tokens=max_tokens,
                    messages=messages,
                    system=system,
                    **kwargs
                )
            except Exception as e:
                print(f"[DualClient] OpenRouter failed, falling back to Anthropic: {e}")
                # Fall back to Anthropic on error

        # Use Anthropic
        print(f"[DualClient] Using Anthropic (call #{self._call_count})")
        kwargs_filtered = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            kwargs_filtered["system"] = system

        return await self.anthropic.messages.create(**kwargs_filtered)

    async def _force_anthropic(
        self,
        model: str,
        max_tokens: int,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        thinking: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Force use of Anthropic API directly (bypasses OpenRouter).

        This is required for features not supported by OpenRouter, such as:
        - Extended thinking (thinking parameter)
        - Streaming with thinking blocks

        Args:
            model: Model ID
            max_tokens: Max tokens
            messages: Message list
            system: System prompt
            thinking: Extended thinking configuration (e.g., {"type": "enabled", "budget_tokens": 8000})

        Returns:
            Claude response from Anthropic API
        """
        self._call_count += 1
        print(f"[DualClient] Forcing Anthropic (call #{self._call_count}) - extended thinking requested")

        api_kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            api_kwargs["system"] = system
        if thinking:
            api_kwargs["thinking"] = thinking

        return await self.anthropic.messages.create(**api_kwargs)

    async def close(self):
        """Close clients."""
        if self.openrouter:
            await self.openrouter.close()
