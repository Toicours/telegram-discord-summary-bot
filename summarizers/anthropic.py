import logging
from anthropic import Anthropic
from summarizers.base import BaseSummarizer

logger = logging.getLogger(__name__)

class AnthropicSummarizer(BaseSummarizer):
    """Anthropic Claude implementation of the summarizer"""
    
    def __init__(self, api_key):
        """
        Initialize with API key
        
        Args:
            api_key (str): Anthropic API key
        """
        super().__init__(api_key)
        self.client = Anthropic(api_key=api_key)
    
    def generate_summary(self, message_texts):
        """
        Generate summary using Anthropic Claude API
        
        Args:
            message_texts (list): List of message texts
            
        Returns:
            str: Generated summary
        """
        try:
            # Combine messages
            combined_text = "\n".join(message_texts)
            
            # Truncate text if too long
            max_tokens = 8000
            if len(combined_text) > max_tokens:
                combined_text = combined_text[-max_tokens:]
            
            # Claude API call
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",  # Claude 3.5 Sonnet model
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize the following conversation, highlighting key topics, notable interactions, and important information:\n\n{combined_text}"
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f'Anthropic summary generation error: {e}')
            return f"Unable to generate summary with Anthropic. Error: {str(e)}"