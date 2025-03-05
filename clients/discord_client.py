import logging
from datetime import datetime
import discord

logger = logging.getLogger(__name__)

class DiscordSummaryClient:
    """Client for posting summaries to Discord"""
    
    def __init__(self, token):
        """
        Initialize Discord client
        
        Args:
            token (str): Discord bot token
        """
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self.token = token
        
        # Store callbacks
        self.on_ready_callbacks = []
    
    def add_on_ready_callback(self, callback):
        """
        Add a callback to run when Discord is ready
        
        Args:
            callback (callable): Async function to call
        """
        self.on_ready_callbacks.append(callback)
    
    async def start(self):
        """Set up event handlers and start the client"""
        
        @self.client.event
        async def on_ready():
            """
            Triggered when Discord client successfully connects
            """
            logger.info(f'Discord client logged in as {self.client.user}')
            
            # Execute all registered callbacks
            for callback in self.on_ready_callbacks:
                await callback()
        
        # Start the client
        await self.client.start(self.token)
    
    async def post_summary(self, channel_id, summary, title="Telegram Channel Summary", provider_name="AI"):
        """
        Post summary to a Discord channel
        
        Args:
            channel_id (int): Discord channel ID
            summary (str): Generated summary
            title (str): Title for the embed
            provider_name (str): Name of the LLM provider
        """
        try:
            # Get the destination channel
            channel = self.client.get_channel(channel_id)
            
            if not channel:
                logger.error(f"Discord channel {channel_id} not found")
                return False
            
            # Format the message
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            embed = discord.Embed(
                title=f"{title} ({current_date})",
                description=summary,
                color=0x3498db
            )
            embed.set_footer(text=f"Summary by {provider_name}")
            
            # Send the message
            await channel.send(embed=embed)
            logger.info(f"Successfully posted summary for '{title}' to Discord channel {channel_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error posting to Discord: {e}")
            return False