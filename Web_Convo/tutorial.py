from nicegui import app, ui
from ui_parts import shell, back_button
@ui.page("/tutorial")
def tutorial_page() -> None:
    with shell("Tutorial"):
        back_button("/")
        ui.label("Application-wide Tutorial").classes("text-3xl font-bold")
        ui.label(
            "Use the tutorial below to learn how the app works from creating and updating a profile, along with using pyfriend."
        ).classes("text-slate-400")
        with ui.card().classes("w-full max-w-3xl mx-auto rounded-lg p-5 gap-4 mt-6"):
            with ui.tabs().classes("w-full"):
                with ui.tab("1. App overview"):
                    ui.markdown(
                        """
                        ### App overview
                        - Start from the home page to choose an existing profile or create a new one.
                        - Use the profile page to review stored traits, interests, notes, and avoids.
                        - Use the update workflow to refresh profile data from a conversation transcript.
                        - Return to this tutorial anytime for guidance.
                        """
                    )
                    ui.button("Go to Home", on_click=lambda: ui.navigate.to("/")).props("color=primary")
                with ui.tab("2. Start"):
                    ui.markdown(
                        """
                        ### Start here
                        - Make a new profile
                        - Use the update flow to refresh the profile with new conversation data.
                        """
                    )
                    ui.button("Go to Profile Create", on_click = lambda: ui.navigate.to("/create")).props("color=primary")
                with ui.tab("3. Profile Creation"):
                    ui.markdown(
                        """
                        ### Paste a transcript
                        - Type the name of the person you have a conversation with (name it first as "test").
                        - Either type traits, interests, avoids and more in the feids below, or
                        - Copy the conversation transcript from a chat or meeting.
                        - for better results, include details about traits, interests, notes, and avoids.
                        - The app will extract the key details automatically.
                        """
                    )
                with ui.tab("4. Update profile"):
                    ui.navigate.to("/update/test")
                    ui.markdown(
                        """
                        ### Update profile
                        - Press **Update Profile**.
                        - The app will analyze the transcript and save the updated profile.
                        - If there is any issue, a notification will display the error.
                        """
                    )
                with ui.tab("5. Pyfriend"):
                    ui.markdown(
                        """
                        ### Using Pyfriend
                        Now, you can use Pyfriend to easily simulate and give specific words, sentences or ideas to say.
                        - You can hit the button and speak (a model will convert the sound into text).
                                                OR
                        - You can directly type the text in.
                        """
                    )
                with ui.tab("6. Usage"):
                    ui.navigate.to("/")
                    ui.markdown(
                        """
                        ### How to use this application
                        This application is mostly used for giving and making points that are suited to the person you want to talk to
                        or in layman's terms, talk perfectly (even if you are an introvert) and talk for a specific person
                        """
                    )
            ui.button("Exit Tutorial", on_click=lambda: ui.navigate.to("/")).classes("mt-4")