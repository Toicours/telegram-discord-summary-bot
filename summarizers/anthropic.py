import logging
from anthropic import Anthropic
from summarizers.base import BaseSummarizer
from utils.prompts import PromptTemplates

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
    
    def generate_summary(
        self, 
        message_texts, 
        topic_name=None, 
        prompt_type=None, 
        override_system_prompt=None, 
        override_user_prompt=None
    ):
        try:
            # Combine messages
            combined_text = "\n".join(message_texts)
            
            # Truncate text if too long
            max_tokens = 8000
            if len(combined_text) > max_tokens:
                combined_text = combined_text[-max_tokens:]
            
            # Get appropriate prompts with potential overrides
            prompts = PromptTemplates.get_prompts(
                topic_name=topic_name, 
                prompt_type=prompt_type,
                override_system_prompt=override_system_prompt,
                override_user_prompt=override_user_prompt
            )
            
            # API call with prompts
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1000,
                system=prompts['system_prompt'],
                messages=[
                    {
                        "role": "user",
                        "content": PromptTemplates.format_user_prompt(
                            combined_text, 
                            topic_name=topic_name,
                            prompt_type=prompt_type,
                            override_system_prompt=override_system_prompt,
                            override_user_prompt=override_user_prompt
                        )
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f'Summary generation error: {e}')
            return f"Unable to generate summary. Error: {str(e)}"