import asyncio
from antigikes import app
from antigcast.config import LOGGER, LOG_CHANNEL_ID
from pyrogram import idle
from antigcast.helpers.tools import checkExpired

async def main():
    try:
        await app.start()
        app.me = await app.get_me()
        username = app.me.username
        namebot = app.me.first_name
        log = await app.send_message(LOG_CHANNEL_ID, "BOT AKTIF!")
        LOGGER("INFO").info(f"{namebot} | [ @{username} ] | 🔥 BERHASIL DIAKTIFKAN! 🔥")
        await log.delete()
    except Exception as e:
        LOGGER("ERROR").error(f"Error while starting bot: {e}")
    LOGGER("INFO").info(f"[🔥 BOT AKTIF! 🔥]")
    await checkExpired()
    await idle()

if __name__ == "__main__":
    LOGGER("INFO").info("Starting Bot...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
