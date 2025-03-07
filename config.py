import os
from enum import Enum
from dotenv import load_dotenv

# Define LLM provider enum
class LLMProvider(Enum):
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"

def load_configuration():
    """
    Load configuration from environment variables
    
    Returns:
        dict: Configuration settings
    """
    # Load environment variables
    load_dotenv()
    
    # Parse topic IDs if provided
    topic_ids_str = os.getenv('TELEGRAM_TOPIC_IDS', '')
    topic_ids = []
    if topic_ids_str:
        topic_ids = [int(id_str) for id_str in topic_ids_str.split(',') if id_str.strip()]
    
    # Determine LLM provider
    llm_provider = LLMProvider(os.getenv('LLM_PROVIDER', 'deepseek'))
    
    # Get the appropriate API key based on the provider
    if llm_provider == LLMProvider.ANTHROPIC:
        llm_api_key = os.getenv('ANTHROPIC_API_KEY')
    elif llm_provider == LLMProvider.DEEPSEEK:
        llm_api_key = os.getenv('DEEPSEEK_API_KEY')
    else:
        llm_api_key = None
    
    # Create configuration dictionary
    config = {
        # Telegram configuration
        'TELEGRAM_API_ID': int(os.getenv('TELEGRAM_API_ID')),
        'TELEGRAM_API_HASH': os.getenv('TELEGRAM_API_HASH'),
        'TELEGRAM_PHONE_NUMBER': os.getenv('TELEGRAM_PHONE_NUMBER'),
        'TELEGRAM_SOURCE_CHANNEL': os.getenv('TELEGRAM_SOURCE_CHANNEL'),
        'TELEGRAM_TOPIC_IDS': topic_ids,  # List of topic IDs to monitor
        'INCLUDE_MAIN_CHANNEL': os.getenv('INCLUDE_MAIN_CHANNEL', 'true').lower() == 'true',
        
        # Message history configuration
        'MESSAGE_HISTORY_DAYS': int(os.getenv('MESSAGE_HISTORY_DAYS', '1')),
        
        # Discord configuration
        'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
        'DISCORD_DESTINATION_CHANNEL_ID': int(os.getenv('DISCORD_DESTINATION_CHANNEL_ID')),
        
        # LLM configuration
        'LLM_PROVIDER': llm_provider,
        'LLM_API_KEY': llm_api_key,
        
        # Provider-specific keys (for reference/debugging)
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        
        # Scheduling
        'SUMMARY_HOUR': int(os.getenv('SUMMARY_HOUR', 23)),
        'SUMMARY_MINUTE': int(os.getenv('SUMMARY_MINUTE', 0))
    }
    
    # Validate LLM configuration
    if not config['LLM_API_KEY']:
        provider_name = config['LLM_PROVIDER'].value.upper()
        raise ValueError(f"Missing API key for {provider_name}. Please set {provider_name}_API_KEY in your .env file.")
    
    return config