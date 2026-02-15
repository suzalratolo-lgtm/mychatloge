import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# --- CONFIGURATION (Loaded from Server Settings) ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
# Target ID must be an integer (e.g., 123456789)
TARGET_USER_ID = int(os.environ.get("TARGET_USER_ID"))

# --- TELEGRAM BOT SETUP ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(from_users=TARGET_USER_ID))
async def handler(event):
    """
    Listens for messages from the specific user and 
    immediately forwards them to 'Saved Messages' (me).
    """
    try:
        sender = await event.get_sender()
        sender_name = sender.first_name if sender else "Unknown"
        
        # Forward the message to your Saved Messages
        # We use 'me' which refers to your own Saved Messages
        await client.send_message("me", f"LOGGED MESSAGE FROM {sender_name}:")
        await client.forward_messages("me", event.message)
        print(f"Captured message from {sender_name}")
    except Exception as e:
        print(f"Error logging message: {e}")

# --- FAKE WEB SERVER (To keep Render awake) ---
async def handle_ping(request):
    return web.Response(text="Bot is Running!")

app = web.Application()
app.router.add_get('/', handle_ping)

# --- MAIN LOOP ---
async def main():
    # Start the Web Server
    runner = web.AppRunner(app)
    await runner.setup()
    # Render assigns a PORT env variable. Default to 8080 if not found.
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

    # Start the Telegram Client
    print("Starting Telegram Client...")
    await client.start()
    print("Telegram Client is Online. Watching for messages...")
    
    # Run forever
    await client.run_until_disconnected()

# PASTE THIS INSTEAD:
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
