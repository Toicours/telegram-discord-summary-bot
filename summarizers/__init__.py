from summarizers.base import BaseSummarizer
from summarizers.deepseek import DeepSeekSummarizer

# Try to import Anthropic if available
try:
    from summarizers.anthropic import AnthropicSummarizer
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

def create_summarizer(provider, api_key):
    """
    Factory function to create the appropriate summarizer
    
    Args:
        provider: LLM provider enum value
        api_key: API key for the provider
        
    Returns:
        A BaseSummarizer instance
    """
    from config import LLMProvider
    
    if provider == LLMProvider.DEEPSEEK:
        return DeepSeekSummarizer(api_key)
    elif provider == LLMProvider.ANTHROPIC:
        if ANTHROPIC_AVAILABLE:
            return AnthropicSummarizer(api_key)
        else:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")