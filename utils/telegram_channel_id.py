import os
import sys
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

async def list_telegram_channels():
    """
    List all Telegram channels and groups the user is a member of,
    using credentials from the .env file
    """
    # Load environment variables
    load_dotenv()
    
    # Get Telegram API credentials from .env
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
    
    if not api_id or not api_hash:
        print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not found in .env file")
        return
    
    print(f"Using API ID: {api_id}")
    print("Connecting to Telegram...")
    
    # Create a new session file specifically for this tool
    client = TelegramClient('channel_finder_session', api_id, api_hash)
    
    try:
        # Start the client but handle the connection differently
        await client.connect()
        
        # Check if already authorized
        if not await client.is_user_authorized():
            print(f"Sending code request to {phone_number}...")
            await client.send_code_request(phone_number)
            
            code = input("Enter the code you received: ")
            try:
                await client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                # This happens when you have two-step verification enabled
                password = input("Two-step verification is enabled. Please enter your password (or press enter to abort): ")
                if not password:
                    print("Operation aborted.")
                    return
                await client.sign_in(password=password)
            except PhoneCodeInvalidError:
                print("The code you entered is invalid. Please try again later.")
                return
        
        print("Connected successfully!")
        
        # List all dialogs (chats, channels, groups)
        print("\n=== CHANNELS AND GROUPS ===")
        print("ID | Type | Name")
        print("-" * 50)
        
        async for dialog in client.iter_dialogs():
            entity_type = "Channel" if dialog.is_channel else "Group" if dialog.is_group else "Chat"
            
            if dialog.is_channel or dialog.is_group:
                print(f"{dialog.id} | {entity_type} | {dialog.name}")
        
        print("\n=== USAGE INSTRUCTIONS ===")
        print("1. Find your channel in the list above")
        print("2. Copy the ID (the number at the beginning of the line)")
        print("3. Update your .env file:")
        print("   TELEGRAM_SOURCE_CHANNEL=CHANNEL_ID_HERE")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nIf you're having trouble with authentication, you can try:")
        print("1. Wait a few hours before trying again (Telegram limits auth attempts)")
        print("2. Use the Telegram web version to find channel IDs manually")
        print("3. Forward a message from the channel to @username_to_id_bot")
    
    finally:
        # Disconnect the client
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(list_telegram_channels())