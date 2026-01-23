import os
from dotenv import load_dotenv

load_dotenv()

API_SECRET = os.getenv('API_SECRET', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
DB_PATH = os.getenv('DB_PATH', 'data/master_scraper.db')

# Autenticación JWT
ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')
JWT_SECRET = os.getenv('JWT_SECRET', API_SECRET or 'dev-secret-change-in-production')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

