"""
Claude API retry wrapper with exponential backoff.

Handles transient errors like rate limits, timeouts, and connection issues.
Supports Claude's extended thinking API for deep reasoning tasks.
"""

import asyncio
from anthropic import RateLimitError, APITimeoutError, APIConnectionError, InternalServerError


# Models that support extended thinking
EXTENDED_THINKING_MODELS = {
    "claude-sonnet-4-5-20250929",
    "claude-opus-4-5-20251101",
}


async def call_claude_with_retry(
    client,
    model: str,
    max_tokens: int,
    messages: list,
    system: str = None,
    thinking_budget: int = None,
    max_retries: int = 3,
    base_delay: float = 0.5  # Reduced from 1.0 for faster recovery
):
    """
    Call Claude API with exponential backoff retry on transient errors.

    Args:
        client: AsyncAnthropic client instance (or DualClaudeClient)
        model: Model name (e.g., "claude-opus-4-5-20251101")
        max_tokens: Maximum tokens in response
        messages: List of message dicts
        system: Optional system prompt
        thinking_budget: Optional token budget for extended thinking (min 1024).
                        When set, enables Claude's native extended thinking mode.
                        Recommended budgets:
                        - 4000: Quick analysis
                        - 8000: Standard synthesis
                        - 16000: Complex multi-source synthesis
        max_retries: Number of retry attempts (default 3)
        base_delay: Base delay in seconds for exponential backoff (default 1.0)

    Returns:
        Claude API response. When thinking_budget is set, response.content
        will contain both thinking blocks and text blocks.

    Raises:
        Original exception after all retries exhausted or on non-retryable errors
    """
    last_error = None

    # Check if client supports extended thinking (DualClaudeClient needs special handling)
    use_extended_thinking = (
        thinking_budget is not None and
        thinking_budget >= 1024 and
        model in EXTENDED_THINKING_MODELS
    )

    for attempt in range(max_retries):
        try:
            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            if system:
                kwargs["system"] = system

            # Add extended thinking parameters if requested
            if use_extended_thinking:
                kwargs["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                }
                print(f"[Claude Retry] Extended thinking enabled with {thinking_budget} token budget")

            # If client is DualClaudeClient and thinking is enabled, force Anthropic
            # (OpenRouter doesn't support extended thinking)
            if use_extended_thinking and hasattr(client, '_force_anthropic'):
                response = await client._force_anthropic(**kwargs)
            else:
                response = await client.messages.create(**kwargs)

            return response

        except (RateLimitError, APITimeoutError, APIConnectionError, InternalServerError) as e:
            last_error = e
            error_type = type(e).__name__

            if attempt == max_retries - 1:
                print(f"[Claude Retry] All {max_retries} attempts failed. Last error: {error_type}: {str(e)[:200]}")
                raise

            delay = base_delay * (2 ** attempt)  # 1s, 2s, 4s
            print(f"[Claude Retry] Attempt {attempt+1}/{max_retries} failed ({error_type}), retrying in {delay}s...")
            await asyncio.sleep(delay)

        except Exception as e:
            # Non-retryable error (e.g., invalid request, auth error)
            print(f"[Claude Retry] Non-retryable error: {type(e).__name__}: {str(e)[:200]}")
            raise

    raise last_error
