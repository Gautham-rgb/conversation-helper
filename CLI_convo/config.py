from pathlib import Path
from dotenv import load_dotenv
import os, CLI_convo.exceptions as exceptions

try:
    # 1. Try root .env (project-wide)
    root_env = Path(__file__).resolve().parent.parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)
    
    # 2. Try legacy api_key.env
    env_path = Path(__file__).resolve().parent / "api_key.env"
    if env_path.exists():
        load_dotenv(env_path)
        
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("api_key")
except Exception as e:
    raise exceptions.GeneralError("The api key you are searching for is unavailable, dead or in a comatose state.")
