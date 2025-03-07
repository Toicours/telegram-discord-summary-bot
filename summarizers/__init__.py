"""
Summarizer Factory Module

This module provides a factory function for creating LLM summarizers and
handles the dynamic selection of appropriate summarizer classes based on 
the configured provider.

The module supports multiple LLM providers and allows easy extensibility
for adding new summarization services.

Key Features:
- Dynamic summarizer creation
- Provider-based selection
- Debugging and tracing of provider selection
"""

from summarizers.base import BaseSummarizer
from summarizers.deepseek import DeepSeekSummarizer
from summarizers.anthropic import AnthropicSummarizer

def create_summarizer(provider, api_key):
    """
    Factory function to create the appropriate LLM summarizer based on the provider.
    
    This function dynamically selects and instantiates a summarizer class 
    (DeepSeek or Anthropic) based on the configured LLM provider. It includes 
    comprehensive debugging to help troubleshoot provider selection.
    
    Args:
        provider (LLMProvider): Enum value specifying the desired LLM provider 
            (either DEEPSEEK or ANTHROPIC).
        api_key (str): API key corresponding to the selected LLM provider.
        
    Returns:
        BaseSummarizer: An instantiated summarizer object ready to generate summaries.
        
    Raises:
        ValueError: If an unsupported LLM provider is specified.
        
    Debugging:
        Prints detailed information about the provider type, value, and comparisons
        to aid in troubleshooting provider selection.
    """
    from config import LLMProvider
    
    print("=" * 50)
    print("DETAILED PROVIDER DEBUGGING:")
    print(f"Provider: {provider}")
    print(f"Provider Type: {type(provider)}")
    print(f"Provider Value: {provider.value}")
    print(f"Provider Comparison (Deepseek): {provider == LLMProvider.DEEPSEEK}")
    print(f"Provider Comparison (Anthropic): {provider == LLMProvider.ANTHROPIC}")
    print("=" * 50)
    
    if provider == LLMProvider.DEEPSEEK:
        return DeepSeekSummarizer(api_key)
    elif provider == LLMProvider.ANTHROPIC:
        return AnthropicSummarizer(api_key)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")