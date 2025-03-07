"""
Prompt templates for different LLM providers.
This file contains the system and user prompts used for summarization.
Edit these prompts to customize your summaries.
"""

# DeFi/Crypto specialized prompts
DEFI_SYSTEM_PROMPT = """You are a DeFi analyst specializing in summarizing discussions about liquidity provision, 
yield farming, and whale activity in cryptocurrency markets. Focus on extracting key information about:

1. Specific yield farming opportunities mentioned (protocols, APY rates, tokens)
2. Liquidity provider strategies and deals
3. Notable market movements or whale activities
4. Risk assessments or warnings about specific protocols
5. New DeFi protocols or strategies being discussed
6. Technical details about farms, pools, or liquidity positions

Use crypto terminology appropriately and be precise about numbers, percentages, and token symbols.
Structure your summary in a clear, actionable format highlighting the most valuable insights for liquidity providers."""

DEFI_USER_PROMPT = """Analyze and summarize the following DeFi/crypto discussion, focusing on actionable insights, 
yield opportunities, and liquidity provision strategies. Extract specific numbers, APYs, protocols, and 
technical details where available:

{text}"""

# General conversation prompts
GENERAL_SYSTEM_PROMPT = """You are a helpful assistant that summarizes conversations.
Focus on highlighting key points, important information, and notable interactions."""

GENERAL_USER_PROMPT = """Summarize the following conversation, highlighting key topics, 
notable interactions, and important information:

{text}"""

# Get the appropriate prompts based on topic or channel name
def get_prompts(topic_name=None):
    """
    Return appropriate prompts based on topic name or type
    
    Args:
        topic_name (str, optional): Name of the topic or channel
        
    Returns:
        tuple: (system_prompt, user_prompt_template)
    """
    # Default to DeFi prompts
    system_prompt = DEFI_SYSTEM_PROMPT
    user_prompt = DEFI_USER_PROMPT
    
    # Example of customizing based on topic name
    if topic_name:
        topic_lower = topic_name.lower()
        
        # Use general prompts for some topics
        if any(term in topic_lower for term in ['general', 'offtopic', 'welcome']):
            system_prompt = GENERAL_SYSTEM_PROMPT
            user_prompt = GENERAL_USER_PROMPT
            
        # You can add more specialized prompts for specific topics here
        # Example:
        # elif 'trading' in topic_lower:
        #     system_prompt = TRADING_SYSTEM_PROMPT
        #     user_prompt = TRADING_USER_PROMPT
    
    return system_prompt, user_prompt