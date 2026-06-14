# conversation-helper
**Stop overthinking your chats. A distraction-free companion for real-time social insights..**
---

## ✨ The Experience
Conversation Helper isn't just a wrapper; it’s a refined interface designed to manage your conversations, preventing problems that even the greatest extroverts may face. 

### 🛡️ Graceful Error Handling
No more cryptic Python crashes. When things go sideways, our custom **Error Engine** translates technical mess into human-readable solutions.
*   **Intelligent Mapping:** Standardized error codes (e.g., `E-401`, `E-NO-PASS`) for instant troubleshooting.
*   **One-Click Recovery:** Integrated "Restart" logic to refresh your session in a heartbeat.
*   **Human-Centric Design:** Error messages that actually make sense (and a few that might make you laugh).
*   and lastly, then reason this was made:
  *   to help you to give your points, ideas and plans like an absolute Extrovert.

---

## 🚀 Getting Started

### 🛠️ System Requirements
- **Python 3.10+**
- **FFmpeg** (Required for audio processing via `pydub`)

### Installation
Clone the repository and step into a cleaner workflow:
```bash
git clone https://github.com/your-repo-path
cd conversation-helper
pip install -r requirements.txt
python -c "import os;os.environ['KERAS_BACKEND'] = 'torch'"
```

### 🔑 Configuration
The application requires several API keys to function. You can provide these in two ways:

#### Option 1: Using a `.env` file (Recommended)
Create a file named `.env` in the root directory and add your keys:
```env
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_service_role_key
ADMIN_EMAILS=admin1@example.com,admin2@example.com
```

#### Option 2: Using Environment Variables
Alternatively, you can export them in your terminal before running the app:
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
export GROQ_API_KEY="your_groq_api_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

### 🚀 Running the App
```bash
# Start the GUI interface
python GUI_convo/GUI.py

# Start the Web interface
python Web_Convo/Web.py

# Start the CLI interface
python CLI_convo/CLI.py
```
---

### Contact
if there is any problem or feedback that has to be fixed or given, please contact: [kaarthikgautham0@gmail.com](mailto:kaarthikgautham0@gmail.com) 
or [gautitheexplorer@gmail.com](mailto:gautitheexplorer@gmail.com)
