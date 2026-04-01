# conversation-helper
**A minimal, distraction-free companion for your LLM workflows.**
---

## ✨ The Experience
Conversation Helper isn't just a wrapper; it’s a refined interface designed to manage your AI context without the clutter. 

### 🛡️ Graceful Error Handling
No more cryptic Python crashes. When things go sideways, our custom **Error Engine** translates technical mess into human-readable solutions.
*   **Intelligent Mapping:** Standardized error codes (e.g., `E-401`, `E-NO-PASS`) for instant troubleshooting.
*   **One-Click Recovery:** Integrated "Restart" logic to refresh your session in a heartbeat.
*   **Human-Centric Design:** Error messages that actually make sense (and a few that might make you laugh).

---

## 🚀 Getting Started

### 🛠️ System Requirements
- **Python 3.10+**
- **FFmpeg** (Required for audio processing via `pydub`)

### Installation
Clone the repository and step into a cleaner workflow:
```bash
git clone https://github.com
cd conversation-helper
// rename config.py.example as config.py
pip install -r requirements.txt
python GUI_convo/GUI.py
