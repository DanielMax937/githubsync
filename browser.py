
import os
from dotenv import load_dotenv
load_dotenv() # 如果使用 .env 文件存储 key
from google import genai

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
