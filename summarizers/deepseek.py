import logging
import time
from openai import OpenAI, APITimeoutError, APIError
from summarizers.base import BaseSummarizer
from utils.prompts import get_prompts

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
        # Configure with shorter timeouts to prevent long-running requests
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=30.0,  # 30 second timeout
            max_retries=2   # Limit retries
        )
    
    def generate_summary(self, message_texts, topic_name=None):
        """
        Generate summary using DeepSeek API (OpenAI-compatible format)
        This is a blocking call that should be run in a separate thread
        
        Args:
            message_texts (list): List of message texts
            topic_name (str, optional): Name of the topic or channel
            
        Returns:
            str: Generated summary
        """
        start_time = time.time()
        
        try:
            # Combine messages (limit length to avoid overloading the API)
            # Keep only most recent messages if there are too many
            if len(message_texts) > 25:
                logger.info(f"Trimming message count from {len(message_texts)} to 25 most recent")
                message_texts = message_texts[-25:]
                
            combined_text = "\n".join(message_texts)
            
            # Limit combined text length
            max_chars = 8000
            if len(combined_text) > max_chars:
                logger.info(f"Truncating combined text from {len(combined_text)} to {max_chars} chars")
                combined_text = combined_text[-max_chars:]
            
            # Log message count
            logger.info(f"Sending {len(message_texts)} messages to DeepSeek API")
            
            # Get appropriate prompts based on topic
            system_prompt, user_prompt_template = get_prompts(topic_name)
            
            # Format the user prompt with the actual text
            user_prompt = user_prompt_template.format(text=combined_text)
            
            # Use OpenAI-compatible format for DeepSeek with timeout
            try:
                # Make the blocking API call
                response = self.client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=1000
                )
                
                # Enhanced logging for successful responses
                elapsed = time.time() - start_time
                logger.info(f"DeepSeek API call completed in {elapsed:.2f} seconds")
                
                # Log more details about the response
                usage_info = "unknown"
                if hasattr(response, 'usage') and response.usage:
                    usage_info = f"prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens}, total: {response.usage.total_tokens}"
                
                logger.info(f"DeepSeek response tokens: {usage_info}")
                logger.info(f"DeepSeek response model: {response.model}")
                
                return response.choices[0].message.content
            
            except APITimeoutError as e:
                logger.error(f"DeepSeek API timeout error details: {str(e)}")
                logger.error(f"Request took more than {self.client.timeout} seconds before timing out")
                
                # Generate a basic fallback summary
                fallback_summary = self._generate_basic_summary(message_texts, topic_name)
                return f"**Summary for {topic_name or 'This Topic'} (Generated from {len(message_texts)} messages)**\n\n{fallback_summary}\n\n*Note: This is a simplified summary due to DeepSeek API timeout.*"
            
            except APIError as e:
                logger.error(f"DeepSeek API error: {e}")
                return f"Unable to generate summary. API error: {str(e)}"
            
        except Exception as e:
            logger.error(f'DeepSeek summary generation error: {e}')
            return f"Unable to generate summary with DeepSeek. Error: {str(e)}"

    def _generate_basic_summary(self, message_texts, topic_name=None):
        """
        Generate a basic summary without using API
        This is a fallback for when the API fails
        
        Args:
            message_texts (list): List of messages
            topic_name (str): Topic name for context
            
        Returns:
            str: Basic summary
        """
        try:
            # Extract authors and message counts
            authors = {}
            topics = set()
            
            for message in message_texts:
                # Try to extract author name
                parts = message.split(':', 1)
                if len(parts) == 2:
                    author = parts[0].strip()
                    content = parts[1].strip()
                    
                    # Count messages per author
                    authors[author] = authors.get(author, 0) + 1
                    
                    # Try to identify topics from key words
                    tokens = content.lower().split()
                    for token in tokens:
                        if len(token) > 5 and token not in ["about", "would", "should", "these", "there", "their", "other"]:
                            topics.add(token)
            
            # Format author information
            author_info = "**Participants**: " + ", ".join([f"{name} ({count})" for name, count in authors.items()])
            
            # Get top topics (if any)
            topic_info = ""
            if topics:
                topic_list = list(topics)[:10]  # Limit to 10 topics
                topic_info = "\n\n**Key terms**: " + ", ".join(topic_list)
            
            # Message stats
            stats = f"\n\n**Messages**: {len(message_texts)} | **Unique Participants**: {len(authors)}"
            
            return f"{author_info}{topic_info}{stats}\n\nConversation happened in {topic_name or 'this channel'}."
            
        except Exception as e:
            logger.error(f"Error generating basic summary: {e}")
            return f"This topic contained {len(message_texts)} messages."