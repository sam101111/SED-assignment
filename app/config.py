import os
from dotenv import load_dotenv

# Use local dotenv file if not running on RENDER
if os.environ.get("RENDER") is None:
    load_dotenv()

# Allows for one central place to define and edit env varibles
class Config:
    bool_map = {"true": True, "false": False}

    SECURE_COOKIES = bool_map.get(os.environ.get("SECURE_COOKIES").strip().lower(), False)
config = Config()