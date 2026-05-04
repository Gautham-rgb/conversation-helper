import os
import socket
from CLI_convo.config import api_key

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
TEXT_MODEL_PATH = os.path.join(MODELS_DIR, "gemma4_4b_it") 
SAMPLE_RATE = 16000

def _check_online(host="8.8.8.8", timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 53))
        return True
    except:
        return False

ONLINE = _check_online() and bool(api_key)

if ONLINE:
    from groq import Groq
    groq_client = Groq(api_key=api_key)
else:
    groq_client = None

GROQ_CHAT_MODEL = "llama-3.3-70b-versatile"
GROQ_WHISPER_MODEL = "whisper-large-v3-turbo"
CHAT_MODEL = GROQ_CHAT_MODEL
WHISPER_MODEL = GROQ_WHISPER_MODEL

_text_model = None

def get_text_model():
    global _text_model
    if _text_model is None:
        import keras_hub
        if not os.path.exists(TEXT_MODEL_PATH):
            raise FileNotFoundError(f"Local Gemma model not found at {TEXT_MODEL_PATH}.")
        _text_model = keras_hub.models.GemmaCausalLM.from_preset(TEXT_MODEL_PATH)
    return _text_model

def gemma_prompt(system, user, history=None):
    """Formats the prompt for Gemma 4's instruction-tuned architecture."""
    turns = f"<start_of_turn>user\n{system}\n\n{user}<end_of_turn>\n"
    for msg in (history or []):
        role = "user" if msg["role"] == "user" else "model"
        turns += f"<start_of_turn>{role}\n{msg['content']}<end_of_turn>\n"
    turns += "<start_of_turn>model\n"
    return turns

def generate(prompt, max_length=512):
    model = get_text_model()
    output = model.generate(prompt, max_length=max_length)
    return output.replace(prompt, "").strip()

def transcribe_offline(wav_path):
    import whisper
    result = whisper.load_model("base").transcribe(wav_path)
    return str(result.get("text", "")).strip()

def save_models():
    import keras_hub
    os.makedirs(MODELS_DIR, exist_ok=True)
    # 2026 Gemma 4 Preset
    keras_hub.models.GemmaCausalLM.from_preset("gemma4_4b_en").save_to_preset(TEXT_MODEL_PATH)
