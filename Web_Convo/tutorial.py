from nicegui import ui
from ui_parts import shell, back_button

def start_tutorial():
    """Trigger to navigate to the tutorial page."""
    ui.notify("Opening Tutorial...")
    ui.navigate.to("/tutorial")

@ui.page("/tutorial")
def tutorial_page() -> None:
    # Use the shell without a tutorial button to prevent nested loops
    with shell("Tutorial"):
        back_button("/")
        ui.label("Application-wide Tutorial").classes("text-3xl font-bold")
        ui.label(
            "Learn how to manage profiles and use Pyfriend with cloud-synced storage."
        ).classes("text-slate-400")
        
        with ui.card().classes("w-full max-w-3xl mx-auto rounded-lg p-5 gap-4 mt-6"):
            with ui.tabs().classes("w-full") as tabs:
                t0 = ui.tab("0. What is this website for?")
                t1 = ui.tab("1. App overview")
                t2 = ui.tab("2. Start")
                t3 = ui.tab("3. Creation")
                t4 = ui.tab("4. SQL Sync")
                t5 = ui.tab("5. Pyfriend")

            with ui.tab_panels(tabs, value=t0).classes('w-full bg-transparent'):
                with ui.tab_panel(t1):
                    ui.markdown("""THIS APP IS FOR BETA TESTING.
                                - People can store other people as 'profiles', made of interests, avoids, notes and personality traits.
                                - You can use these profiles to simulate a conversation or find perfect conversation starters using this website, Echo - Clear.
                                - You can even store previous conversations as that profile's 'history'.
                                - This can allow you to speak with absolute certainty and make points that resonate with the listener.""")
                with ui.tab_panel(t1):
                    ui.markdown("### App Overview\n- Choose profiles or create new ones.\n- Data is stored locally for the app and backed up to SQL.")
                    ui.button("Go Home", on_click=lambda: ui.navigate.to("/")).props("color=primary")
                
                with ui.tab_panel(t2):
                    ui.markdown("### Start Here\n- Create a new profile identity.\n- Use the update flow to refresh profile data.")
                    ui.button("Create Profile", on_click=lambda: ui.navigate.to("/create")).props("color=primary")
                
                with ui.tab_panel(t3):
                    ui.markdown("### Profile Creation\n- Enter traits, interests, and avoids.\n- The AI can extract these from conversation transcripts automatically.")
                
                with ui.tab_panel(t4):
                    ui.markdown("### Update & SQL Sync\n- Saving updates your local `profiles.json` immediately.\n- A backup is simultaneously sent to Supabase SQL for safety.")
                
                with ui.tab_panel(t5):
                    ui.markdown("""### Using Pyfriend
                                - Simulate conversations tailored to specific profiles.
                                - Use voice-to-text or manual typing.
                                - You can now use 'tags', that allow pyfriend to focus on specific things like:
                                    - @person(X) - focuses on person X
                                    - @conversation(X, Y) - tries to think about whether X and Y can talk to each other perfectly.""")
                    ui.button("Go to Pyfriend", on_click =lambda: ui.navigate.to("/all_pyfriend"))

        ui.button("Exit Tutorial", on_click=lambda: ui.navigate.to("/")).classes("mt-4")