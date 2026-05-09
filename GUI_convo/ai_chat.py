import threading
import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText
from app import root, show, set_scrolled_text, append_scrolled_text
from CLI_convo.profile_storage import Profile
from CLI_convo.offline import ONLINE, groq_client, generate, gemma_prompt, GROQ_CHAT_MODEL


def ai_chat(name=""):
    try:
        profile = Profile.load(name)
        if not profile:
            from error_page import error_page
            show(error_page, error_message="Profile not found.")
            return

        history: list[dict] = []

        ttk.Button(root, text="← Back", bootstyle="secondary-link",
                   command=lambda: _back(name)).pack(anchor="w", padx=16, pady=12)
        ttk.Label(root, text=f"AI Chat — {name}",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16)

        chat_box = ScrolledText(root, height=20, autohide=True, state="disabled", wrap="word")
        chat_box.pack(fill="both", expand=True, padx=16, pady=8)

        input_row = ttk.Frame(root, padding=8)
        input_row.pack(fill="x", padx=16)
        msg_entry = ttk.Entry(input_row, font=("Segoe UI", 11))
        msg_entry.pack(side="left", fill="x", expand=True)
        msg_entry.bind("<Return>", lambda e: _send(profile, msg_entry, chat_box, history))
        
        ttk.Button(input_row, text="Send", bootstyle="primary",
                   command=lambda: _send(profile, msg_entry, chat_box, history)).pack(side="left", padx=8)

        mode = "Online (Groq)" if ONLINE else "Offline (Local Gemma)"
        set_scrolled_text(chat_box, f"System: Chatting with {name}'s profile.\nMode: {mode}.\n\n")

        msg_entry.focus_set()

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _send(profile, msg_entry, chat_box, history):
    msg = msg_entry.get().strip()
    if not msg:
        return

    msg_entry.delete(0, "end")
    append_scrolled_text(chat_box, f"You: {msg}\n\n")
    history.append({"role": "user", "content": msg})
    msg_entry.config(state="disabled")

    def task():
        system = f"You are a social intelligence assistant.\n{profile.to_prompt(query=msg) if profile else 'No profile loaded.'}"
        try:
            if ONLINE and groq_client:
                response = groq_client.chat.completions.create(
                    model=GROQ_CHAT_MODEL,
                    messages=[{"role": "system", "content": system}] + history,
                )
                reply = response.choices[0].message.content or ""
            else:
                # Use last user message + history
                reply = generate(
                    gemma_prompt(system, history[-1]["content"], history[:-1]),
                    max_length=600
                )

            history.append({"role": "assistant", "content": reply})
            root.after(0, lambda: append_scrolled_text(chat_box, f"AI: {reply}\n\n"))
        except Exception as e:
            root.after(0, lambda: append_scrolled_text(chat_box, f"Error: {str(e)}\n\n"))
        finally:
            root.after(0, lambda: msg_entry.config(state="normal"))
            root.after(0, msg_entry.focus_set)

    threading.Thread(target=task, daemon=True).start()


def _back(name):
    from profile_page import profile_page
    show(profile_page, name=name)