import os
import asyncio
import logging
import concurrent.futures
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

# Create a thread pool executor for running blocking LLM calls
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=5)

class TelegramToDiscordBot:
    """Main application that ties together Telegram, Discord, and summarization"""
    
    def __init__(self, config):
        """Initialize the application"""
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
        
        # Store mapping of topic IDs to names
        self.topic_names = {}
        
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
        
        # Run immediately on startup
        logger.info("Running initial summary generation")
        asyncio.create_task(self._generate_and_post_summary())
    
    async def _run_in_thread(self, func, *args, **kwargs):
        """
        Run a blocking function in a separate thread
        
        Args:
            func: The function to run
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The result of the function
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(thread_pool, func, *args, **kwargs)
    
    async def _generate_and_post_summary(self):
        """Generate and post daily summary for all configured topics"""
        try:
            channel_id = self.config['TELEGRAM_SOURCE_CHANNEL']
            topic_ids = self.config['TELEGRAM_TOPIC_IDS']
            include_main = self.config['INCLUDE_MAIN_CHANNEL']
            history_days = self.config['MESSAGE_HISTORY_DAYS']  # Get history period from config
            
            # Track all messages and collections
            all_messages = []
            message_collections = {}
            
            # Collect forum topics if we have topic IDs
            if topic_ids:
                topics = await self.telegram_client.get_forum_topics(channel_id)
                # Create a mapping of topic_id to topic_title
                for topic in topics:
                    self.topic_names[topic.id] = topic.title
            
            # Collect messages from all channels in parallel
            collection_tasks = []
            
            # Add main channel task if requested
            if include_main:
                logger.info(f"Collecting messages from main channel (past {history_days} days)")
                main_channel_task = self.telegram_client.collect_messages(
                    channel_identifier=channel_id,
                    days=history_days  # Pass history period
                )
                collection_tasks.append(("Main Channel", main_channel_task))
            
            # Add tasks for each topic
            for topic_id in topic_ids:
                logger.info(f"Collecting messages from topic {topic_id} (past {history_days} days)")
                topic_name = self.topic_names.get(topic_id, f"Topic {topic_id}")
                topic_task = self.telegram_client.collect_messages(
                    channel_identifier=channel_id,
                    topic_id=topic_id,
                    days=history_days  # Pass history period
                )
                collection_tasks.append((topic_name, topic_task))
            
            # Wait for all collection tasks to complete
            for topic_name, task in collection_tasks:
                messages = await task
                if messages:
                    all_messages.extend(messages)
                    message_collections[topic_name] = messages
            
            # Now generate and post summaries in parallel
            summary_tasks = []
            
            # Process each collection
            for title, messages in message_collections.items():
                if messages:
                    task = asyncio.create_task(
                        self._process_and_post_summary(
                            messages=messages,
                            title=title,
                            topic_name=title
                        )
                    )
                    summary_tasks.append(task)
            
            # Generate overall summary if we have multiple collections
            if len(message_collections) > 1 and all_messages:
                task = asyncio.create_task(
                    self._process_and_post_summary(
                        messages=all_messages,
                        title="All Channels and Topics",
                        topic_name="All"
                    )
                )
                summary_tasks.append(task)
            
            # Wait for all summary tasks to complete with a timeout
            if summary_tasks:
                # Use as_completed to process results as they finish
                for task in asyncio.as_completed(summary_tasks, timeout=300):
                    try:
                        await task
                    except asyncio.TimeoutError:
                        logger.error("A summary task timed out after 5 minutes")
                    except Exception as e:
                        logger.error(f"Error in summary task: {e}")
            else:
                logger.info("No messages found to summarize in any channel or topic")
        
        except Exception as e:
            logger.error(f'Daily summary generation and posting failed: {e}')
    
    async def _process_and_post_summary(self, messages, title, topic_name=None):
        """
        Process messages and post summary for a specific topic or channel
        
        Args:
            messages (list): List of messages to summarize
            title (str): Title for the summary (e.g., topic name)
            topic_name (str, optional): Name of the topic for prompt selection
        """
        if not messages:
            logger.info(f"No messages found to summarize for {title}")
            return False
        
        try:
            # Generate summary in a separate thread to avoid blocking
            logger.info(f"Generating summary for {title} with {len(messages)} messages")
            
            # Run the blocking API call in a separate thread
            def generate_summary_thread():
                try:
                    return self.summarizer.generate_summary(messages, topic_name)
                except Exception as e:
                    logger.error(f"Error generating summary for {title}: {e}")
                    return f"Unable to generate summary for {title}. Error: {str(e)}"
            
            # Run with a longer timeout (120 seconds instead of 60)
            try:
                # Wait for the summary with a timeout
                summary = await asyncio.wait_for(
                    self._run_in_thread(generate_summary_thread),
                    timeout=120  # Increased timeout to 120 seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"Summary generation for {title} timed out after 120 seconds")
                
                # Generate a simple summary
                participant_count = len(set([msg.split(':')[0].strip() for msg in messages if ':' in msg]))
                summary = f"**Summary for {title}**\n\n" + \
                        f"This conversation had {len(messages)} messages from approximately {participant_count} participants.\n\n" + \
                        f"*Note: Unable to generate a detailed summary due to DeepSeek API timeout.*"
            
            # Post to Discord
            provider_name = self.config['LLM_PROVIDER'].name.capitalize()
            await self.discord_client.post_summary(
                channel_id=self.config['DISCORD_DESTINATION_CHANNEL_ID'],
                summary=summary,
                title=f"Telegram Summary: {title}",
                provider_name=provider_name
            )
            return True
            
        except Exception as e:
            logger.error(f"Error processing summary for {title}: {e}")
            return False
    
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