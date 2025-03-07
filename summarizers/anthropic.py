import logging
from anthropic import Anthropic
from summarizers.base import BaseSummarizer
from utils.prompts import get_prompts

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
    
    def generate_summary(self, message_texts, topic_name=None):
        """
        Generate summary using Anthropic Claude API
        
        Args:
            message_texts (list): List of message texts
            topic_name (str, optional): Name of the topic or channel
            
        Returns:
            str: Generated summary
        """
        try:
            # Combine messages
            combined_text = "\n".join(message_texts)
            
            # Get appropriate prompts based on topic
            system_prompt, user_prompt_template = get_prompts(topic_name)
            
            # Format the user prompt with the actual text
            user_prompt = user_prompt_template.format(text=combined_text)
            
            # Log message count
            logger.info(f"Sending {len(message_texts)} messages to Anthropic API")
            
            # Claude API call
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            logger.info("Successfully received response from Anthropic API")
            return response.content[0].text
        
        except Exception as e:
            logger.error(f'Anthropic summary generation error: {e}')
            return f"Unable to generate summary with Anthropic. Error: {str(e)}"