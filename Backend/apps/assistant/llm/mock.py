"""
Mock LLM Provider for offline testing, local development, and test environments.
Provides deterministic, evidence-grounded responses without requiring external API keys.
"""
import re
from apps.assistant.llm.base import BaseLLMProvider
from apps.assistant.prompts import INSUFFICIENT_EVIDENCE_MESSAGE


class MockLLMProvider(BaseLLMProvider):
    """
    Simulates a compliant legal assistant LLM by extracting grounded facts
    directly from the prompt's retrieved evidence sections.
    """

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Check if evidence was supplied in the prompt
        if "No judicial evidence excerpts available." in user_prompt or "[Evidence 1]" not in user_prompt:
            return INSUFFICIENT_EVIDENCE_MESSAGE

        # Extract Evidence blocks from the prompt
        evidence_blocks = re.findall(
            r'--- \[Evidence (\d+)\] ---\s*Case:\s*([^\n]+)\s*Document:\s*([^\n]+)\s*Excerpt:\s*(.*?)(?=(?:--- \[Evidence|\n+INSTRUCTIONS|$))',
            user_prompt,
            re.DOTALL
        )

        if not evidence_blocks:
            return INSUFFICIENT_EVIDENCE_MESSAGE

        # Build grounded synthesis
        response_parts = [
            "Based strictly on the judicial records retrieved from the NYAYASETU repository:\n"
        ]

        for num, case_info, doc_info, excerpt in evidence_blocks:
            clean_excerpt = excerpt.strip().replace("\n", " ")
            if len(clean_excerpt) > 250:
                clean_excerpt = clean_excerpt[:247] + "..."
            response_parts.append(
                f"- [Evidence {num}]: In {case_info} ({doc_info}), the document records:\n"
                f"  \"{clean_excerpt}\"\n"
            )

        response_parts.append(
            "Note: The information above is derived entirely from the retrieved case excerpts on record."
        )

        return "\n".join(response_parts)

