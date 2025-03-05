import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

async def test_channel_access():
    """
    Test if we can access the channel with the current ID format
    """
    # Load environment variables
    load_dotenv()
    
    # Get credentials from .env
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
    channel_id_str = os.getenv('TELEGRAM_SOURCE_CHANNEL')
    
    print(f"Testing connection to channel: {channel_id_str}")
    
    # Create client
    client = TelegramClient('test_session', api_id, api_hash)
    
    try:
        # Start the client
        await client.start(phone=phone_number)
        print("Connected to Telegram")
        
        # Try different formats
        formats_to_try = [
            channel_id_str,  # Original format
            int(channel_id_str) if channel_id_str.lstrip('-').isdigit() else None,  # As integer
        ]
        
        # Add -100 prefix format if needed
        if channel_id_str.lstrip('-').isdigit():
            if channel_id_str.startswith('-'):
                base_id = channel_id_str[1:]
                formats_to_try.append(int(f"-100{base_id}"))
            elif not channel_id_str.startswith('-100'):
                formats_to_try.append(int(f"-100{channel_id_str}"))
        
        # Remove -100 prefix if present
        if channel_id_str.startswith('-100') and channel_id_str[4:].isdigit():
            formats_to_try.append(int(channel_id_str[4:]))
        
        # Filter out None values
        formats_to_try = [fmt for fmt in formats_to_try if fmt is not None]
        
        # Try each format
        for i, format_to_try in enumerate(formats_to_try):
            print(f"\nTesting format {i+1}: {format_to_try} (type: {type(format_to_try).__name__})")
            try:
                entity = await client.get_entity(format_to_try)
                print(f"SUCCESS! Found channel: {entity.title}")
                print(f"Channel type: {type(entity).__name__}")
                print(f"Use this format in your .env: TELEGRAM_SOURCE_CHANNEL={format_to_try}")
                
                # Get some message
                print("\nTrying to fetch a message...")
                messages = await client.get_messages(entity, limit=1)
                if messages and len(messages) > 0:
                    print(f"Successfully fetched a message from {entity.title}!")
                else:
                    print("No messages found or no access to messages.")
                
                break
            except Exception as e:
                print(f"Failed: {str(e)}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Disconnect
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_channel_access())