import os
from dotenv import load_dotenv

class Config:
    load_dotenv()
    # If its not set it will default to false, allowing the pipeline to run
    if os.environ.get("RENDER") is None:
        SECURE_COOKIES = False
    else:
        SECURE_COOKIES = True
 
config = Config()