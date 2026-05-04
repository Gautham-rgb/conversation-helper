from pathlib import Path
from dotenv import load_dotenv
import os, CLI_convo.exceptions as exceptions

try:
    env_path = Path(__file__).resolve().parent / "api_key.env"
    load_dotenv(env_path)
    api_key = os.getenv("api_key") or os.getenv("GROQ_API_KEY")
except Exception as e:
    raise exceptions.GeneralError("The api key you are searching for is unavailable, dead or in a comatose state.")
