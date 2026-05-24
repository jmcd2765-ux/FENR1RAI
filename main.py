import logging
import os
import sys
from pathlib import Path

# Setup logging before any other imports
from logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables with fallback
try:
    from dotenv import load_dotenv
    load_dotenv()
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning("No .env file found. Copy .env.example to .env and configure it.")
except ImportError:
    logger.warning("python-dotenv not installed. Environment variables must be set manually.")
    logger.warning("Run: pip install python-dotenv")

from twitch_bot import FENR1RBot

if __name__ == "__main__":
    try:
        logger.info("FENR1R Bot starting up...")
        Fenr1r = FENR1RBot()
        logger.info("FENR1R Bot initialized, connecting to Twitch...")
        Fenr1r.run()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Make sure .env file exists with TWITCH_ACCESS_TOKEN and TWITCH_CHANNEL set.")
        logger.error("Copy .env.example to .env and fill in your values.")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("FENR1R stopped by user.")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        sys.exit(1)
