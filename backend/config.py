import os
from dotenv import load_dotenv

load_dotenv()

API_SECRET = os.getenv('API_SECRET', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
DB_PATH = os.getenv('DB_PATH', 'data/master_scraper.db')

