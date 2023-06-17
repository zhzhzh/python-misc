import os

from dotenv import load_dotenv

load_dotenv('.env.local')

print(os.getenv('LOCAL_TEST_DB'))

print(os.getenv('NON_EXIST', 'NA'))
