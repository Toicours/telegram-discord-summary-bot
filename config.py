import os
from enum import Enum
from dotenv import load_dotenv

class LLMProvider(Enum):
    """
    Enumeration of supported Large Language Model (LLM) providers.
    
    Defines the available LLM providers that can be used for text summarization.
    Each provider is associated with a specific string value for configuration.
    
    Attributes:
        DEEPSEEK (str): Represents the DeepSeek LLM provider.
        ANTHROPIC (str): Represents the Anthropic Claude LLM provider.
    """
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"

def load_configuration():
    """
    Load and validate configuration from environment variables.
    
    This function performs the following key tasks:
    - Loads environment variables from .env file
    - Parses and validates configuration settings
    - Converts configuration values to appropriate types
    - Retrieves API keys based on selected LLM provider
    
    Returns:
        dict: A comprehensive configuration dictionary containing:
            - Telegram API credentials
            - Discord bot configuration
            - LLM provider settings
            - Scheduling parameters
    
    Raises:
        ValueError: If critical configuration values are missing or invalid
        TypeError: If configuration values cannot be converted to required types
    """
    # Force load .env file and override existing environment variables
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path, override=True)
    
    # Debug prints
    print("DEBUG: Detailed LLM Provider Information:")
    print(f"os.getenv('LLM_PROVIDER'): {repr(os.getenv('LLM_PROVIDER'))}")
    print(f"ENUM Values: {[p.value for p in LLMProvider]}")
    
    # Determine LLM provider
    try:
        # Try to get from environment, but default to Anthropic if not set
        llm_provider_str = os.getenv('LLM_PROVIDER', 'anthropic').strip().lower()
        llm_provider = LLMProvider(llm_provider_str)
        print(f"DEBUG: Parsed LLM Provider: {llm_provider}")
        print(f"DEBUG: LLM Provider Type: {type(llm_provider)}")
    except ValueError:
        print(f"ERROR: Invalid LLM Provider: '{llm_provider_str}'. Defaulting to Anthropic.")
        llm_provider = LLMProvider.ANTHROPIC
    
    # Create configuration dictionary
    config = {
        # Telegram configuration
        'TELEGRAM_API_ID': int(os.getenv('TELEGRAM_API_ID')),
        'TELEGRAM_API_HASH': os.getenv('TELEGRAM_API_HASH'),
        'TELEGRAM_PHONE_NUMBER': os.getenv('TELEGRAM_PHONE_NUMBER'),
        'TELEGRAM_SOURCE_CHANNEL': os.getenv('TELEGRAM_SOURCE_CHANNEL'),
        'TELEGRAM_TOPIC_IDS': [int(id_str) for id_str in os.getenv('TELEGRAM_TOPIC_IDS', '').split(',') if id_str.strip()],
        'INCLUDE_MAIN_CHANNEL': os.getenv('INCLUDE_MAIN_CHANNEL', 'true').lower() == 'true',
        
        # Discord configuration
        'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
        'DISCORD_DESTINATION_CHANNEL_ID': int(os.getenv('DISCORD_DESTINATION_CHANNEL_ID')),
        
        # LLM configuration
        'LLM_PROVIDER': llm_provider,
        'LLM_API_KEY': _get_llm_api_key(llm_provider),
        
        # Scheduling
        'SUMMARY_HOUR': int(os.getenv('SUMMARY_HOUR', 23)),
        'SUMMARY_MINUTE': int(os.getenv('SUMMARY_MINUTE', 0))
    }
    
    return config

def _get_llm_api_key(provider):
    """
    Retrieve the appropriate API key based on the selected LLM provider.
    
    This function securely retrieves the API key for the specified LLM provider
    from environment variables. It supports different providers and ensures
    that a valid API key is available.
    
    Args:
        provider (LLMProvider): The selected LLM provider enum value.
    
    Returns:
        str: The API key for the specified provider.
    
    Raises:
        ValueError: If no API key is found for the specified provider.
    """
    print(f"DEBUG: Getting API key for provider: {provider}")
    
    if provider == LLMProvider.ANTHROPIC:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        print("DEBUG: Selected Anthropic API Key")
    elif provider == LLMProvider.DEEPSEEK:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        print("DEBUG: Selected DeepSeek API Key")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    if not api_key:
        raise ValueError(f"No API key found for {provider.value} provider")
    
    return api_key