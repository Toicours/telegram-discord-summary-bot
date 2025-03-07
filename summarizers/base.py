import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseSummarizer(ABC):
    """Base class for all summarizers"""
    
    def __init__(self, api_key):
        """
        Initialize with API key
        
        Args:
            api_key (str): API key for the service
        """
        self.api_key = api_key
    
    @abstractmethod
    def generate_summary(self, message_texts, topic_name=None):
        """
        Generate a summary from message texts
        
        Args:
            message_texts (list): List of text messages
            topic_name (str, optional): Name of the topic or channel
            
        Returns:
            str: Generated summary
        """
        pass