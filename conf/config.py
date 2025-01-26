from dotenv import load_dotenv
import os
load_dotenv('conf/.env')
SAVE_PATH = os.getenv("SAVE_PATH", "./data/")
LOG_PATH = os.getenv("LOG_PATH", "./logs/")
SQL_PATH = os.getenv("SQL_PATH", "./sql/")
SESSION_PATH = os.getenv("SESSION_PATH", "./session/")
BOT_TOKEN = os.getenv("BOT_TOKEN", "null")
API_ID = int(os.getenv("API_ID", "null"))
API_HASH = os.getenv("API_HASH", "null")
LSKY_API = os.getenv("LSKY_API", "https://img.pmxu.xyz/api/v1")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "pmxmaster")
BOT_USERNAME = os.getenv("BOT_USERNAME", "yaoyue_lskybot")
LSKY_VERSION = os.getenv("LSKY_VERSION", "paid")
