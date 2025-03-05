import logging
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.functions.channels import GetForumTopicsRequest
from telethon.tl.types import Channel, Message

logger = logging.getLogger(__name__)

class TelegramChannelClient:
    """Client for interacting with Telegram channels and topics"""
    
    def __init__(self, api_id, api_hash, phone_number, session_name='telegram_to_discord_bot'):
        """
        Initialize Telegram client
        
        Args:
            api_id (int): Telegram API ID
            api_hash (str): Telegram API hash
            phone_number (str): Phone number for authentication
            session_name (str): Name for the session file
        """
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.phone_number = phone_number
        # Store the channel entity once found for reuse
        self._channel_entity_cache = {}
    
    async def start(self):
        """Start the Telegram client"""
        await self.client.start(phone=self.phone_number)
        logger.info("Telegram client started")
    
    async def _get_channel_entity(self, channel_id):
        """
        Get channel entity with multiple format attempts
        
        Args:
            channel_id: Channel ID in various possible formats
            
        Returns:
            The channel entity or None if not found
        """
        # Check cache first
        if channel_id in self._channel_entity_cache:
            return self._channel_entity_cache[channel_id]
            
        channel_id_str = str(channel_id)
        channel_entity = None
        errors = []
        
        # Attempt 1: Try as is (string or int)
        try:
            channel_entity = await self.client.get_entity(channel_id)
        except Exception as e:
            errors.append(f"Original format failed: {str(e)}")
        
        # Attempt 2: If it's a string that starts with -100, try without that prefix
        if not channel_entity and channel_id_str.startswith('-100') and channel_id_str[4:].isdigit():
            try:
                peer_id = int(channel_id_str[4:])
                channel_entity = await self.client.get_entity(peer_id)
            except Exception as e:
                errors.append(f"Without -100 prefix failed: {str(e)}")
        
        # Attempt 3: If numeric but doesn't start with -100, try adding that prefix
        if not channel_entity and channel_id_str.lstrip('-').isdigit() and not channel_id_str.startswith('-100'):
            # Handle cases with just - prefix
            if channel_id_str.startswith('-'):
                base_id = channel_id_str[1:]
            else:
                base_id = channel_id_str
                
            try:
                peer_id = int(f"-100{base_id}")
                channel_entity = await self.client.get_entity(peer_id)
            except Exception as e:
                errors.append(f"With -100 prefix failed: {str(e)}")
        
        if not channel_entity:
            error_msg = f"Cannot find channel with ID {channel_id}. Tried multiple formats."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Cache the entity for future use
        self._channel_entity_cache[channel_id] = channel_entity
        return channel_entity
    
    async def get_forum_topics(self, channel_id):
        """
        Get all topics in a forum (supergroup with topics)
        
        Args:
            channel_id: Channel or supergroup ID
            
        Returns:
            list: List of topic objects
        """
        try:
            # Get the channel entity
            channel_entity = await self._get_channel_entity(channel_id)
            
            # Check if this is a forum (supergroup with topics)
            if not hasattr(channel_entity, 'forum') or not channel_entity.forum:
                logger.info(f"Channel {channel_id} is not a forum/group with topics")
                return []
            
            # Get all topics in the forum
            topics_result = await self.client(GetForumTopicsRequest(
                channel=channel_entity,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100  # Maximum limit, might need pagination for very large forums
            ))
            
            logger.info(f"Found {len(topics_result.topics)} topics in forum {channel_entity.title}")
            return topics_result.topics
            
        except Exception as e:
            logger.error(f"Error getting forum topics: {e}")
            return []
    
    async def collect_messages(self, channel_identifier, topic_id=None, days=1):
        """
        Collect messages from a channel/group and optionally from a specific topic
        
        Args:
            channel_identifier (str/int): Channel username or ID
            topic_id (int, optional): Topic ID within the forum
            days (int): Number of days to look back
            
        Returns:
            list: List of message texts with sender information
        """
        try:
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(days=days)
            
            # Get the channel entity using our robust method
            channel_entity = await self._get_channel_entity(channel_identifier)
            
            # Collect messages
            message_texts = []
            
            # If topic_id is provided, collect messages from that topic
            if topic_id is not None:
                async for message in self.client.iter_messages(
                    channel_entity,
                    offset_date=time_threshold,
                    reverse=True,
                    reply_to=topic_id  # This filters for messages in the specific topic
                ):
                    if not message.text:
                        continue
                    
                    # Get sender info
                    sender = await self._get_sender_display_name(message)
                    message_texts.append(f"{sender}: {message.text}")
            else:
                # Collect messages from the main channel/group
                async for message in self.client.iter_messages(
                    channel_entity,
                    offset_date=time_threshold,
                    reverse=True
                ):
                    if not message.text:
                        continue
                    
                    # Get sender info
                    sender = await self._get_sender_display_name(message)
                    message_texts.append(f"{sender}: {message.text}")
            
            logger.info(f"Collected {len(message_texts)} messages from {channel_entity.title}" + 
                      (f" topic {topic_id}" if topic_id else ""))
            return message_texts
        
        except Exception as e:
            logger.error(f'Error collecting Telegram messages: {e}')
            return []
    
    async def _get_sender_display_name(self, message):
        """
        Get the display name for a message sender
        
        Args:
            message: Telegram message object
            
        Returns:
            str: Display name for the sender
        """
        if not message.sender:
            return "Unknown"
            
        if hasattr(message.sender, 'username') and message.sender.username:
            return f"@{message.sender.username}"
        elif hasattr(message.sender, 'first_name') and message.sender.first_name:
            if hasattr(message.sender, 'last_name') and message.sender.last_name:
                return f"{message.sender.first_name} {message.sender.last_name}"
            return message.sender.first_name
        
        return str(message.sender_id)