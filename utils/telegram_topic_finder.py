import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.channels import GetForumTopicsRequest

async def list_telegram_topics():
    """
    List all topics in a Telegram forum/supergroup using credentials from the .env file
    """
    # Load environment variables
    load_dotenv()
    
    # Get Telegram API credentials from .env
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
    channel_id_str = os.getenv('TELEGRAM_SOURCE_CHANNEL')
    
    if not api_id or not api_hash or not channel_id_str:
        print("Error: TELEGRAM_API_ID, TELEGRAM_API_HASH, or TELEGRAM_SOURCE_CHANNEL not found in .env file")
        return
    
    print(f"Using API ID: {api_id}")
    print(f"Using channel ID: {channel_id_str}")
    print("Connecting to Telegram...")
    
    # Create the client
    client = TelegramClient('topic_finder_session', api_id, api_hash)
    
    try:
        # Start the client
        await client.start(phone=phone_number)
        print("Connected successfully!")
        
        # Get the channel entity with multiple attempts at different formats
        channel_entity = None
        errors = []
        
        # Attempt 1: Try as is (string)
        try:
            channel_entity = await client.get_entity(channel_id_str)
            print(f"Found channel using original string format: {channel_id_str}")
        except Exception as e:
            errors.append(f"String format failed: {str(e)}")
        
        # Attempt 2: Try as integer
        if not channel_entity and channel_id_str.lstrip('-').isdigit():
            try:
                channel_id_int = int(channel_id_str)
                channel_entity = await client.get_entity(channel_id_int)
                print(f"Found channel using integer format: {channel_id_int}")
            except Exception as e:
                errors.append(f"Integer format failed: {str(e)}")
        
        # Attempt 3: Try without -100 prefix if it has one
        if not channel_entity and channel_id_str.startswith('-100') and channel_id_str[4:].isdigit():
            try:
                peer_id = int(channel_id_str[4:])
                channel_entity = await client.get_entity(peer_id)
                print(f"Found channel using ID without -100 prefix: {peer_id}")
            except Exception as e:
                errors.append(f"Without -100 prefix failed: {str(e)}")
        
        # Attempt 4: Try with -100 prefix if it doesn't have one and is numeric
        if not channel_entity and channel_id_str.lstrip('-').isdigit() and not channel_id_str.startswith('-100'):
            # If it has a negative sign but not -100
            if channel_id_str.startswith('-'):
                base_id = channel_id_str[1:]
            else:
                base_id = channel_id_str
                
            try:
                peer_id = int(f"-100{base_id}")
                channel_entity = await client.get_entity(peer_id)
                print(f"Found channel using ID with -100 prefix: {peer_id}")
            except Exception as e:
                errors.append(f"With -100 prefix failed: {str(e)}")
        
        # If still not found, list available dialogs to help user
        if not channel_entity:
            print("\nCould not find the channel with any of these formats:")
            for error in errors:
                print(f"  - {error}")
            
            print("\nHere are the channels/groups you have access to:")
            print("ID | Type | Name")
            print("-" * 50)
            
            async for dialog in client.iter_dialogs():
                entity_type = "Channel" if dialog.is_channel else "Group" if dialog.is_group else "Chat"
                
                if dialog.is_channel or dialog.is_group:
                    print(f"{dialog.id} | {entity_type} | {dialog.name}")
            
            print("\nTry using one of these IDs in your .env file")
            return
        
        # Check if this is a forum (supergroup with topics)
        if not hasattr(channel_entity, 'forum') or not channel_entity.forum:
            print(f"The channel '{channel_entity.title}' is not a forum/group with topics")
            return
        
        print(f"Found forum: {channel_entity.title}")
        
        # Get all topics in the forum
        topics_result = await client(GetForumTopicsRequest(
            channel=channel_entity,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=100  # Maximum limit
        ))
        
        # Print all topics
        print("\n=== TOPICS IN FORUM ===")
        print("ID | Title")
        print("-" * 50)
        
        for topic in topics_result.topics:
            print(f"{topic.id} | {topic.title}")
        
        print("\n=== USAGE INSTRUCTIONS ===")
        print("1. Copy the IDs of the topics you want to monitor")
        print("2. Update your .env file:")
        print("   TELEGRAM_TOPIC_IDS=111,222,333")
        print("   (Replace with your actual topic IDs)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect the client
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(list_telegram_topics())