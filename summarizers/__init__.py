"""
Summarizer Factory Module

This module provides a factory function for creating LLM summarizers and
handles the selection of appropriate summarizer classes based on the provider.
"""

from summarizers.base import BaseSummarizer
from summarizers.deepseek import DeepSeekSummarizer
from summarizers.anthropic import AnthropicSummarizer

ANTHROPIC_AVAILABLE = True

def create_summarizer(provider, api_key):
    """
    Factory function to create the appropriate LLM summarizer based on the provider.
    
    Dynamically selects and instantiates a summarizer class (DeepSeek or Anthropic)
    based on the configured LLM provider. Includes debug print statements to help
    troubleshoot provider selection.
    
    Args:
        provider (LLMProvider): Enum value specifying the desired LLM provider 
            (either DEEPSEEK or ANTHROPIC).
        api_key (str): API key corresponding to the selected LLM provider.
        
    Returns:
        BaseSummarizer: An instantiated summarizer object ready to generate summaries.
        
    Raises:
        ValueError: If an unsupported LLM provider is specified.
        
    Debugging:
        Prints debug information about the provider type, value, and comparisons.
    """
    from config import LLMProvider
    
    print(f"DEBUG: Provider type: {type(provider)}")
    print(f"DEBUG: Provider value: {provider}")
    print(f"DEBUG: Provider comparison (Deepseek): {provider == LLMProvider.DEEPSEEK}")
    print(f"DEBUG: Provider comparison (Anthropic): {provider == LLMProvider.ANTHROPIC}")
    
    if provider == LLMProvider.DEEPSEEK:
        return DeepSeekSummarizer(api_key)
    elif provider == LLMProvider.ANTHROPIC:
        return AnthropicSummarizer(api_key)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")