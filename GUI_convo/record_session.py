import os
import tkinter as tk
import threading
import tempfile
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from app import root, show
from CLI_convo.CLI import build_profile, transcribe
from CLI_convo.offline import SAMPLE_RATE

try:
    import sounddevice as sd
    import soundfile as sf
    _MIC_AVAILABLE = True
except ImportError:
    _MIC_AVAILABLE = False

try:
    from pydub import AudioSegment
    _PYDUB_AVAILABLE = True
except ImportError:
    _PYDUB_AVAILABLE = False


def record_session(name=""):
    try:
        ttk.Button(root, text="<- Back", bootstyle="secondary-link",
                   command=lambda: _back(name)).pack(anchor="w", padx=16, pady=12)
        ttk.Label(root, text=f"Record Session — {name}",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16)
        ttk.Label(root, text="Record live audio or upload a file to update the profile.",
                  bootstyle="secondary").pack(anchor="w", padx=16, pady=(2, 16))

        # Microphone section
        mic_outer = tk.LabelFrame(root, text="Microphone Recording")
        mic_outer.pack(fill="x", padx=16, pady=(0, 12))
        mic_inner = ttk.Frame(mic_outer, padding=12)
        mic_inner.pack(fill="x")

        if not _MIC_AVAILABLE:
            ttk.Label(mic_inner, text="sounddevice and soundfile required.\n"
                                      "Install: pip install sounddevice soundfile",
                      bootstyle="warning").pack(anchor="w")
        else:
            _build_mic_section(mic_inner, name)

        # File upload section
        file_outer = tk.LabelFrame(root, text="Upload Audio File")
        file_outer.pack(fill="x", padx=16, pady=(0, 12))
        file_inner = ttk.Frame(file_outer, padding=12)
        file_inner.pack(fill="x")
        _build_file_section(file_inner, name)

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _build_mic_section(parent, name):
    dur_row = ttk.Frame(parent)
    dur_row.pack(anchor="w", pady=(0, 8))
    ttk.Label(dur_row, text="Duration (seconds):").pack(side="left")
    dur_var = ttk.IntVar(value=30)
    ttk.Spinbox(dur_row, from_=5, to=300, textvariable=dur_var, width=6).pack(side="left", padx=8)

    status_lbl = ttk.Label(parent, text="Ready.", bootstyle="secondary")
    status_lbl.pack(anchor="w", pady=(0, 6))

    progress = ttk.Progressbar(parent, mode="determinate", length=400)
    progress.pack(anchor="w", pady=(0, 8))

    rec_btn = ttk.Button(parent, text="Start Recording", bootstyle="danger", width=20)
    rec_btn.pack(anchor="w")

    state = {"active": False, "audio": None}

    def _start():
        if state["active"]:
            return
        duration = dur_var.get()
        state["active"] = True
        rec_btn.config(state="disabled", text="Recording...")
        progress["value"] = 0
        status_lbl.config(text="Recording... speak clearly.", bootstyle="danger")

        def _record():
            audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                           channels=1, dtype="int16")
            sd.wait()
            state["audio"] = (audio, SAMPLE_RATE)
            state["active"] = False
            root.after(0, _on_done)

        threading.Thread(target=_record, daemon=True).start()

    def _on_done():
        progress["value"] = 100
        status_lbl.config(text="Processing...", bootstyle="info")
        rec_btn.config(state="normal", text="Start Recording")

        audio, sr = state["audio"]
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()

        def _process():
            try:
                sf.write(tmp.name, audio, sr)
                text = transcribe(tmp.name)
                build_profile(name, text, name)
                root.after(0, lambda: _finish(status_lbl, tmp.name, name))
            except Exception as e:
                root.after(0, lambda: messagebox.showerror("Error", str(e)))
                root.after(0, lambda: status_lbl.config(text="Failed.", bootstyle="danger"))
            finally:
                try:
                    os.unlink(tmp.name)
                except OSError:
                    pass

        threading.Thread(target=_process, daemon=True).start()

    rec_btn.config(command=_start)


def _build_file_section(parent, name):
    SUPPORTED = [("Audio Files", "*.wav *.mp3 *.m4a *.ogg *.flac *.aac"), ("All Files", "*.*")]

    file_lbl = ttk.Label(parent, text="No file selected.", bootstyle="secondary")
    file_lbl.pack(anchor="w", pady=(0, 8))

    status_lbl = ttk.Label(parent, text="", bootstyle="secondary")
    status_lbl.pack(anchor="w", pady=(0, 6))

    process_btn = ttk.Button(parent, text="Select & Process File", bootstyle="primary", width=24)
    process_btn.pack(anchor="w")

    def _pick():
        path = filedialog.askopenfilename(filetypes=SUPPORTED)
        if not path:
            return
        file_lbl.config(text=os.path.basename(path), bootstyle="info")
        process_btn.config(state="disabled")
        status_lbl.config(text="Processing...", bootstyle="info")

        def _process():
            try:
                wav_path = _ensure_wav(path)
                text = transcribe(wav_path)
                build_profile(name, text, name)
                if wav_path != path:
                    try:
                        os.unlink(wav_path)
                    except OSError:
                        pass
                root.after(0, lambda: _finish(status_lbl, path, name))
            except Exception as e:
                root.after(0, lambda: messagebox.showerror("Error", str(e)))
                root.after(0, lambda: status_lbl.config(text="Failed.", bootstyle="danger"))
                root.after(0, lambda: process_btn.config(state="normal"))

        threading.Thread(target=_process, daemon=True).start()

    process_btn.config(command=_pick)


def _ensure_wav(path: str) -> str:
    if path.lower().endswith(".wav"):
        return path
    if not _PYDUB_AVAILABLE:
        raise RuntimeError("pydub is required for non-WAV files.\nInstall: pip install pydub")
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    ext = os.path.splitext(path)[1].lstrip(".").lower() or "mp3"
    AudioSegment.from_file(path, format=ext).export(tmp.name, format="wav")
    return tmp.name


def _finish(status_lbl, path, name):
    status_lbl.config(text=f"Done — updated from '{os.path.basename(path)}'.", bootstyle="success")
    messagebox.showinfo("Success", f"{name}'s profile has been updated.")
    _back(name)


def _back(name):
    from profile_page import profile_page
    show(profile_page, name=name)