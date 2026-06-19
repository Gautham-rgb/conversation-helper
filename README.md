# 💬 Conversation Helper
**Stop overthinking your social life. A low-key companion that helps you navigate real-time interactions with confidence.**

---

## ✨ What is this?
Let's be real: not everyone is a natural extrovert. Whether it's a high-stakes meeting, a first date, or just trying to keep a conversation flowing, we've all had those "what do I say next?" moments.

**Conversation Helper** is designed to bridge that gap. It's not just a tool; it's like having a socially-aware wingman in your pocket. It helps you track personality traits, remember interests, and get AI-powered suggestions so you can bring your best, most confident self to every interaction.

### 🛡️ We've got your back (Graceful Error Handling)
Nothing kills the vibe like a cryptic `Traceback (most recent call last):`. We've built a custom **Error Engine** that turns technical glitches into human conversations.
*   **No More Code-Speak:** Instead of `E-401`, you'll get a helpful nudge to check your login.
*   **Quick Fixes:** Integrated recovery logic to get you back in the game instantly.
*   **Actually Useful:** Error messages that guide you toward a solution (and maybe a little humor along the way).

---

## 🚀 Get Up and Running

### 🛠️ The Basics
Before you dive in, make sure you have these installed:
- **Python 3.10+**
- **FFmpeg** (Necessary for audio processing via `pydub`)

### Installation
Grab the code and set up your environment in a few quick steps:
```bash
git clone https://github.com/your-repo-path
cd conversation-helper
pip install -r requirements.txt
# Set the backend to torch for optimal performance
python -c "import os;os.environ['KERAS_BACKEND'] = 'torch'"
```

### 🔑 Setting Up Your Keys
The app needs a few API keys to work its magic. You've got two ways to do this:

#### Option 1
Create a `.env` file in the root directory. Just copy-paste this and add your keys:
```env
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_service_role_key
ADMIN_EMAILS=admin1@example.com,admin2@example.com
```

#### Option 2
If you're just testing things out, you can export them directly in your terminal:
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
export GROQ_API_KEY="your_groq_api_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

### 🎮 Pick Your Interface
Depending on where you are, choose how you want to interact with the helper:
```bash
# For the full visual experience (Desktop)
python GUI_convo/GUI.py

# For the modern, browser-based feel (Web)
python Web_Convo/Web.py

# For the lean, fast, terminal-style flow (CLI)
python CLI_convo/CLI.py
```

---

### 👋 Get in Touch
Found a bug? Have a brilliant idea to make this even better? I'd love to hear from you!
Reach out to: [kaarthikgautham0@gmail.com](mailto:kaarthikgautham0@gmail.com) or [gautitheexplorer@gmail.com](mailto:gautitheexplorer@gmail.com)
