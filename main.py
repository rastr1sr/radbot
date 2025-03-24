import os
from dotenv import load_dotenv
import sys

from bot.bot import RadioMonashBot
from bot.utils.ffmpeg import check_and_install_ffmpeg
from bot.utils.logger import get_logger

logger = get_logger("Main")

def main():
    load_dotenv()
    if not check_and_install_ffmpeg():
        logger.critical("FFmpeg is required but could not be installed automatically. Please install FFmpeg manually.")
        sys.exit("ERROR: FFmpeg is required but could not be installed. Please install FFmpeg manually.")
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.critical("No Discord token found in environment variables!")
        sys.exit("ERROR: DISCORD_TOKEN environment variable not set!")
    
    try:
        logger.info("Starting Radio Monash Discord bot...")
        bot = RadioMonashBot()
        bot.run(token, log_handler=None)
    except Exception as e:
        logger.critical(f"Error starting bot: {e}")

if __name__ == "__main__":
    main()
