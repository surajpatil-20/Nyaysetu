"""
Base abstraction for LLM providers in NYAYASETU.
"""
from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM text generation providers.
    """

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate text given a system prompt and a user prompt.

        Args:
            system_prompt: System directive / persona.
            user_prompt: Grounded user prompt including evidence.

        Returns:
            Generated response string.
        """
        pass

