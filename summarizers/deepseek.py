import logging
from openai import OpenAI
from summarizers.base import BaseSummarizer

# Get logger
logger = logging.getLogger(__name__)

class DeepSeekSummarizer(BaseSummarizer):
    """DeepSeek implementation of the summarizer using OpenAI-compatible format"""
    
    def __init__(self, api_key):
        """
        Initialize with API key
        
        Args:
            api_key (str): DeepSeek API key
        """
        super().__init__(api_key)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def generate_summary(self, message_texts):
        """
        Generate summary using DeepSeek API (OpenAI-compatible format)
        
        Args:
            message_texts (list): List of message texts
            
        Returns:
            str: Generated summary
        """
        try:
            # Combine messages
            combined_text = "\n".join(message_texts)
            
            # Log message count
            logger.info(f"Sending {len(message_texts)} messages to DeepSeek API")
            
            # Use OpenAI-compatible format for DeepSeek with specialized DeFi prompt
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a DeFi analyst specializing in summarizing discussions about liquidity provision, 
                        yield farming, and whale activity in cryptocurrency markets. Focus on extracting key information about:
                        
                        1. Specific yield farming opportunities mentioned (protocols, APY rates, tokens)
                        2. Liquidity provider strategies and deals
                        3. Notable market movements or whale activities
                        4. Risk assessments or warnings about specific protocols
                        5. New DeFi protocols or strategies being discussed
                        6. Technical details about farms, pools, or liquidity positions
                        
                        Use crypto terminology appropriately and be precise about numbers, percentages, and token symbols.
                        Structure your summary in a clear, actionable format highlighting the most valuable insights for liquidity providers."""
                    },
                    {
                        "role": "user", 
                        "content": f"""Analyze and summarize the following DeFi/crypto discussion, focusing on actionable insights, 
                        yield opportunities, and liquidity provision strategies. Extract specific numbers, APYs, protocols, and 
                        technical details where available:

                        {combined_text}"""
                    }
                ],
                max_tokens=1000
            )
            
            logger.info("Successfully received response from DeepSeek API")
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f'DeepSeek summary generation error: {e}')
            return f"Unable to generate summary with DeepSeek. Error: {str(e)}"