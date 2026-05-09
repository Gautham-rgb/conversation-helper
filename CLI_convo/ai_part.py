from CLI_convo.profile_storage import Profile   # fixed: was flat import
from CLI_convo.offline import ONLINE, groq_client, generate, gemma_prompt, GROQ_CHAT_MODEL


def suggest(profile: Profile, situation: str) -> str:
    user_content = (
        f"{profile.to_prompt(query=situation)}\n\n"
        f"Situation: {situation}\n\n"
        f"Give 3 things to say, 1 thing to avoid, and 1 wildcard move. "
        f"Be concise. No markdown bold."
    )
    system_content = (
        "You are a social intelligence assistant. "
        "Give tailored conversation suggestions based on the person's profile. "
        "No markdown bold."
    )

    if ONLINE and groq_client:
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user",   "content": user_content},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[ai_part] Groq failed, falling back offline: {e}")

    return generate(gemma_prompt(system_content, user_content), max_length=600)