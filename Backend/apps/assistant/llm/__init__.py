"""
LLM Provider Factory for NYAYASETU.
"""
import logging
from django.conf import settings
from apps.assistant.llm.base import BaseLLMProvider
from apps.assistant.llm.mock import MockLLMProvider
from apps.assistant.llm.gemini import GeminiLLMProvider
from apps.assistant.llm.openai import OpenAILLMProvider

logger = logging.getLogger(__name__)


def get_llm_provider() -> BaseLLMProvider:
    """
    Instantiate the configured LLM provider according to Django settings.
    Defaults to MockLLMProvider if not configured or keys missing.
    """
    provider_name = getattr(settings, "LLM_PROVIDER", "mock").lower().strip()
    api_key = getattr(settings, "LLM_API_KEY", "").strip()
    model_name = getattr(settings, "LLM_MODEL", "").strip()

    if provider_name == "gemini":
        if not api_key:
            logger.warning("LLM_PROVIDER='gemini' requested but LLM_API_KEY is empty. Falling back to MockLLMProvider.")
            return MockLLMProvider()
        return GeminiLLMProvider(api_key=api_key, model_name=model_name or "gemini-1.5-flash")

    elif provider_name in ("openai", "groq", "ollama", "vllm"):
        if not api_key and provider_name not in ("ollama",):
            logger.warning("LLM_PROVIDER='%s' requested but LLM_API_KEY is empty. Falling back to MockLLMProvider.", provider_name)
            return MockLLMProvider()
        return OpenAILLMProvider(api_key=api_key, model_name=model_name or "gpt-4o-mini")

    elif provider_name == "mock":
        return MockLLMProvider()

    else:
        logger.warning("Unknown LLM_PROVIDER '%s'. Defaulting to MockLLMProvider.", provider_name)
        return MockLLMProvider()


__all__ = ["BaseLLMProvider", "MockLLMProvider", "GeminiLLMProvider", "OpenAILLMProvider", "get_llm_provider"]

