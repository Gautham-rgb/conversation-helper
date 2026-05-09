"""Tutorial page for GUI_convo - explains how to use the application."""
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import ttk as tkk
from app import root, show

def tutorial():
    """Display the tutorial page."""
    try:
        # Back button
        ttk.Button(root, text="← Back to Home", bootstyle="secondary-link",
                   command=_back).pack(anchor="w", padx=16, pady=12)
        
        # Title
        ttk.Label(root, text="Tutorial", 
                  font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=16)
        
        ttk.Label(root, text="Learn how to use Conversation Manager with cloud sync.",
                  font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(0, 12))
        
        # Create a scrollable frame for the tutorial content
        canvas = tk.Canvas(root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        scrollbar.pack(side="right", fill="y")
        
        # Tutorial sections
        sections = [
            ("0. What is this app for?", 
             "This app helps you manage social connections by storing profiles of people.\n\n"
             "• Store profiles with traits, interests, notes, and things to avoid\n"
             "• Simulate conversations using AI (Pyfriend)\n"
             "• Log real conversations to build history\n"
             "• Get AI-powered conversation suggestions\n"
             "• Cloud sync keeps your data safe and accessible across devices"),
            
            ("1. Creating a Profile",
             "Click '+ New Profile' on the home screen.\n\n"
             "• Enter the person's name\n"
             "• Add traits (e.g., 'introverted', 'humorous')\n"
             "• List interests (e.g., 'gaming', 'cooking')\n"
             "• Add notes about them\n"
             "• Note things to avoid in conversation\n\n"
             "OR paste a conversation transcript and let AI extract the profile!"),
            
            ("2. Using Pyfriend",
             "Pyfriend is your AI conversation coach.\n\n"
             "• Select a profile to talk about\n"
             "• Describe your situation (type or speak)\n"
             "• Get tailored conversation advice\n"
             "• Use voice input by holding the mic button\n\n"
             "Pro tip: In 'Ask All' mode, you can use tags:\n"
             "  @person(Name) - focus on specific person\n"
             "  @conversation(Person1, Person2) - analyze compatibility"),
            
            ("3. Live Session",
             "Get real-time suggestions during conversations.\n\n"
             "• Describe the current situation\n"
             "• Click 'Get Suggestion' for AI advice\n"
             "• After the conversation, log it to build history\n"
             "• Rate the outcome (good/neutral/bad)"),
            
            ("4. Cloud Sync",
             "Your data is automatically backed up to the cloud.\n\n"
             "• Profiles are saved locally AND to Supabase\n"
             "• Access your profiles from any device\n"
             "• History and RAG data are synced\n"
             "• Works offline with local fallback"),
            
            ("5. Updating Profiles",
             "Keep profiles fresh with new information.\n\n"
             "• Go to a profile page\n"
             "• Click 'Update' or 'Edit'\n"
             "• Paste a new conversation transcript\n"
             "• AI will extract and add new traits/interests"),
            
            ("6. History & RAG",
             "Your conversation history powers smarter AI responses.\n\n"
             "• Log conversations after live sessions\n"
             "• RAG (Retrieval-Augmented Generation) uses history\n"
             "• AI references past conversations for context\n"
             "• More history = better, more personalized advice")
        ]
        
        # Create sections in the scrollable frame
        for i, (title, content) in enumerate(sections):
            # Section card
            card = ttk.Frame(scrollable_frame, bootstyle="light", padding=15)
            card.pack(fill="x", padx=8, pady=6)
            
            # Section title
            ttk.Label(card, text=title, font=("Segoe UI", 13, "bold"),
                      bootstyle="inverse-light").pack(anchor="w")
            
            # Section content
            content_label = ttk.Label(card, text=content, wraplength=600,
                                      justify="left", bootstyle="secondary")
            content_label.pack(anchor="w", pady=(8, 0))
        
        # Navigation buttons at the bottom
        nav_frame = ttk.Frame(scrollable_frame, padding=10)
        nav_frame.pack(fill="x", padx=8, pady=12)
        
        ttk.Button(nav_frame, text="Create Your First Profile", bootstyle="success",
                   command=lambda: _navigate_to_create()).pack(side="left", padx=4)
        ttk.Button(nav_frame, text="Try Pyfriend", bootstyle="primary",
                   command=lambda: _navigate_to_all_pyfriend()).pack(side="left", padx=4)
        
    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))

def _back():
    from home import home
    show(home)

def _navigate_to_create():
    from create_profile import create_profile
    show(create_profile)

def _navigate_to_all_pyfriend():
    from all_pyfriend import all_pyfriend_page
    show(all_pyfriend_page)