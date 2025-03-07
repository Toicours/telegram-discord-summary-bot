import os
from enum import Enum
from dotenv import load_dotenv

class LLMProvider(Enum):
    """
    Enumeration of supported Large Language Model (LLM) providers.
    
    Attributes:
        DEEPSEEK: Represents the DeepSeek LLM provider.
        ANTHROPIC: Represents the Anthropic Claude LLM provider.
    """
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"

def load_configuration():
    """
    Load and validate configuration from environment variables.
    
    This function reads configuration settings from .env file, performs 
    type conversions, and sets default values where necessary.
    
    Returns:
        dict: A comprehensive configuration dictionary containing 
              settings for Telegram, Discord, LLM, and scheduling.
    
    Raises:
        ValueError: If critical configuration values are missing or invalid.
    """
    # Load environment variables
    load_dotenv()
    
    # Debug: Print all environment variables related to LLM configuration
    print("DEBUG: LLM_PROVIDER env var:", os.getenv('LLM_PROVIDER'))
    
    # Parse topic IDs if provided
    topic_ids_str = os.getenv('TELEGRAM_TOPIC_IDS', '')
    topic_ids = []
    if topic_ids_str:
        topic_ids = [int(id_str) for id_str in topic_ids_str.split(',') if id_str.strip()]
    
    # Determine LLM provider with default fallback
    llm_provider = LLMProvider(os.getenv('LLM_PROVIDER', 'deepseek'))
    
    # Debug: Print detailed LLM provider information
    print(f"DEBUG: Loaded LLM Provider: {llm_provider}")
    print(f"DEBUG: LLM Provider Type: {type(llm_provider)}")
    
    # Create configuration dictionary
    config = {
        # Telegram configuration
        'TELEGRAM_API_ID': int(os.getenv('TELEGRAM_API_ID')),
        'TELEGRAM_API_HASH': os.getenv('TELEGRAM_API_HASH'),
        'TELEGRAM_PHONE_NUMBER': os.getenv('TELEGRAM_PHONE_NUMBER'),
        'TELEGRAM_SOURCE_CHANNEL': os.getenv('TELEGRAM_SOURCE_CHANNEL'),
        'TELEGRAM_TOPIC_IDS': topic_ids,  # List of topic IDs to monitor
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
    
    Args:
        provider (LLMProvider): The selected LLM provider.
    
    Returns:
        str: The API key for the specified provider.
    
    Raises:
        ValueError: If no API key is found for the specified provider.
    """
    if provider == LLMProvider.ANTHROPIC:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        print("DEBUG: Using Anthropic API Key")
    elif provider == LLMProvider.DEEPSEEK:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        print("DEBUG: Using DeepSeek API Key")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    if not api_key:
        raise ValueError(f"No API key found for {provider.value} provider")
    
    return api_key