import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Local imports
from config import load_configuration
from utils.logging_config import setup_logging
from summarizers import create_summarizer
from clients.telegram_client import TelegramChannelClient
from clients.discord_client import DiscordSummaryClient

# Set up logging
logger = setup_logging()

class TelegramToDiscordBot:
    """Main application that ties together Telegram, Discord, and summarization"""
    
    def __init__(self, config):
        """
        Initialize the application
        
        Args:
            config (dict): Application configuration
        """
        self.config = config
        
        # Initialize the telegram client
        self.telegram_client = TelegramChannelClient(
            api_id=config['TELEGRAM_API_ID'],
            api_hash=config['TELEGRAM_API_HASH'],
            phone_number=config['TELEGRAM_PHONE_NUMBER']
        )
        
        # Initialize the discord client
        self.discord_client = DiscordSummaryClient(
            token=config['DISCORD_TOKEN']
        )
        
        # Initialize the summarizer
        self.summarizer = create_summarizer(
            provider=config['LLM_PROVIDER'],
            api_key=config['LLM_API_KEY']
        )
        
        # Initialize the scheduler
        self.scheduler = AsyncIOScheduler()
        
        # Register Discord ready callback
        self.discord_client.add_on_ready_callback(self._setup_scheduler)
    
    async def _setup_scheduler(self):
        """Set up the scheduler for daily summaries"""
        self.scheduler.add_job(
            self._generate_and_post_summary,
            'cron',
            hour=self.config.get('SUMMARY_HOUR', 23),
            minute=self.config.get('SUMMARY_MINUTE', 0)
        )
        
        logger.info(
            f"Scheduled daily summary at {self.config.get('SUMMARY_HOUR', 23)}:"
            f"{self.config.get('SUMMARY_MINUTE', 0)}"
        )
        self.scheduler.start()
        
        # Add this line to run immediately for testing
        asyncio.create_task(self._generate_and_post_summary())
    
    async def _generate_and_post_summary(self):
        """Generate and post daily summary for all configured topics"""
        try:
            channel_id = self.config['TELEGRAM_SOURCE_CHANNEL']
            topic_ids = self.config['TELEGRAM_TOPIC_IDS']
            include_main = self.config['INCLUDE_MAIN_CHANNEL']
            
            all_messages = []
            topic_names = {}
            
            # Collect forum topics if we have topic IDs
            if topic_ids:
                topics = await self.telegram_client.get_forum_topics(channel_id)
                # Create a mapping of topic_id to topic_title
                for topic in topics:
                    topic_names[topic.id] = topic.title
            
            # Collect messages from main channel if requested
            if include_main:
                logger.info(f"Collecting messages from main channel")
                main_messages = await self.telegram_client.collect_messages(
                    channel_identifier=channel_id
                )
                
                if main_messages:
                    all_messages.extend(main_messages)
                    await self._process_and_post_summary(
                        messages=main_messages,
                        title="Main Channel"
                    )
            
            # Collect messages from each topic
            for topic_id in topic_ids:
                logger.info(f"Collecting messages from topic {topic_id}")
                topic_messages = await self.telegram_client.collect_messages(
                    channel_identifier=channel_id,
                    topic_id=topic_id
                )
                
                if topic_messages:
                    all_messages.extend(topic_messages)
                    topic_title = topic_names.get(topic_id, f"Topic {topic_id}")
                    await self._process_and_post_summary(
                        messages=topic_messages,
                        title=topic_title
                    )
            
            # If we have topics, also create an overall summary
            if len(topic_ids) > 0 and all_messages:
                await self._process_and_post_summary(
                    messages=all_messages,
                    title="All Channels and Topics"
                )
            
            if not all_messages:
                logger.info("No messages found to summarize in any channel or topic")
        
        except Exception as e:
            logger.error(f'Daily summary generation and posting failed: {e}')
    
    async def _process_and_post_summary(
        self, 
        messages, 
        title, 
        prompt_type=None, 
        override_system_prompt=None, 
        override_user_prompt=None
    ):
        """
        Process messages and post summary for a specific topic or channel
        
        Args:
            messages (list): List of messages to summarize
            title (str): Title for the summary (e.g., topic name)
            prompt_type (str, optional): Explicitly specify prompt type
            override_system_prompt (str, optional): Custom system prompt
            override_user_prompt (str, optional): Custom user prompt
        """
        if not messages:
            logger.info(f"No messages found to summarize for {title}")
            return
        
        # Generate summary with additional prompt options
        summary = self.summarizer.generate_summary(
            messages, 
            topic_name=title, 
            prompt_type=prompt_type,
            override_system_prompt=override_system_prompt,
            override_user_prompt=override_user_prompt
        )
        
        # Post to Discord
        provider_name = self.config['LLM_PROVIDER'].name.capitalize()
        await self.discord_client.post_summary(
            channel_id=self.config['DISCORD_DESTINATION_CHANNEL_ID'],
            summary=summary,
            title=f"Telegram Summary: {title}",
            provider_name=provider_name
        )
    
    async def start(self):
        """Start the bot services"""
        # Start Telegram client
        await self.telegram_client.start()
        
        # Start Discord client
        await self.discord_client.start()

async def main():
    """Main application entry point"""
    try:
        # Load configuration
        config = load_configuration()
        
        # Create and start the bot
        bot = TelegramToDiscordBot(config)
        await bot.start()
    
    except Exception as e:
        logger.error(f"Application startup failed: {e}")

if __name__ == '__main__':
    asyncio.run(main())