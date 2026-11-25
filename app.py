import os
import streamlit as st

try:
    from google import genai
except Exception:
    genai = None

st.set_page_config(
    page_title="MindBridge AI",
    page_icon="🧠",
    layout="centered",
)

st.markdown("""
<style>
.block-container {
    max-width: 850px;
    padding-top: 2rem;
}
.hero {
    padding: 1.5rem;
    border-radius: 18px;
    background: linear-gradient(120deg, #e6f5fb, #e9eaff);
    border: 1px solid #cbdcf3;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>🧠 MindBridge AI</h1>'
    '<h3>A supportive bridge to mental well-being</h3>'
    '<p>Accessible mental health information, reflective check-ins, '
    'and guidance on finding human support.</p></div>',
    unsafe_allow_html=True
)

st.warning(
    "MindBridge AI is an early prototype for education and general support. "
    "It is not a therapist, medical service, diagnostic tool, or emergency service. "
    "Do not enter your full name, address, phone number, or other identifying details."
)

with st.expander("When you need urgent help"):
    st.write(
        "If you may harm yourself or someone else, or you are in immediate danger, "
        "please contact local emergency services or go to the nearest hospital now. "
        "If possible, tell a trusted person who can stay with you. "
        "Do not rely on this prototype for crisis support."
    )

st.subheader("Your well-being check-in")

mood = st.select_slider(
    "How are you feeling right now?",
    options=["Very low", "Low", "Okay", "Good", "Very good"],
    value="Okay"
)

stress = st.select_slider(
    "How intense does your stress feel today?",
    options=["Not at all", "A little", "Moderate", "High", "Very high"],
    value="Moderate"
)

if st.button("Reflect on my check-in"):
    st.info(
        f"You selected {mood} for your mood and {stress} for stress. "
        "There is no right or wrong answer. Consider one small supportive step: "
        "take a short break, drink water, write down what is on your mind, "
        "or speak with someone you trust. If these feelings persist or affect daily "
        "life, consider reaching out to a qualified mental health professional."
    )

st.divider()

st.subheader("Talk to the MindBridge assistant")

st.caption(
    "Ask for general information about stress, anxiety, low mood, "
    "or ways to seek support."
)

SYSTEM_PROMPT = """
You are MindBridge AI, a calm, respectful mental-well-being information assistant.

You are not a therapist, doctor, or emergency service.

Never diagnose, prescribe, or claim to treat a condition.

Offer general, practical, low-risk coping ideas and encourage qualified
professional support when symptoms are persistent, severe, or interfere
with daily life.

Do not ask for identifying information.

Avoid judgement and stigma.

If the user indicates imminent self-harm, suicide intent, harm to another
person, or immediate danger, respond compassionately and encourage them
to contact local emergency services or go to the nearest hospital immediately.

Encourage them to reach a trusted person who can stay with them.

Do not imply that you can monitor or rescue them.

Keep responses concise and clear.
"""


def local_reply(message):

    msg = message.lower()

    crisis_terms = [
        "kill myself",
        "suicide",
        "end my life",
        "hurt myself",
        "self harm",
        "harm myself",
        "want to die",
        "kill someone"
    ]

    if any(term in msg for term in crisis_terms):
        return (
            "I'm sorry things feel so difficult right now. "
            "Your safety matters. If you may act on these thoughts "
            "or are in immediate danger, contact local emergency "
            "services or go to the nearest hospital now. Please tell "
            "a trusted person and ask them to stay with you. "
            "If you can do so safely, move away from anything you "
            "might use to hurt yourself or someone else. "
            "This prototype cannot provide emergency care."
        )

    if "anxiety" in msg or "anxious" in msg or "panic" in msg:
        return (
            "Anxiety can feel overwhelming. You could try grounding "
            "yourself: notice five things you can see, four you can "
            "feel, three you can hear, two you can smell, and one "
            "you can taste. Breathe gently and slowly, without "
            "forcing it. If anxiety is frequent, intense, or "
            "disrupting daily life, consider speaking with a "
            "qualified professional."
        )

    if "depress" in msg or "sad" in msg or "low mood" in msg:
        return (
            "I'm sorry you're having a hard time. If it feels "
            "manageable, choose one small step for now: talk with "
            "someone you trust, eat or drink something, or spend "
            "a little time somewhere you feel safe. Ongoing low "
            "mood deserves support from a qualified mental health "
            "professional. You do not have to manage it alone."
        )

    if "stress" in msg or "overwhelm" in msg:
        return (
            "When everything feels overwhelming, try choosing "
            "just one small task you can do in the next ten minutes. "
            "A short pause, gentle movement, or talking with "
            "someone supportive may also help. If stress is "
            "persistently affecting your sleep, health, or daily "
            "activities, consider professional support."
        )

    return (
        "Thank you for sharing that. I can offer general "
        "well-being information, but I cannot diagnose or replace "
        "professional care. What feels most useful right now: "
        "understanding what you are experiencing, trying a simple "
        "coping strategy, or finding out how to seek human support?"
    )


if "messages" not in st.session_state:
    st.session_state.messages = []


for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])


prompt = st.chat_input(
    "Type a question about emotional well-being..."
)

if prompt:

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    response = None

    if api_key and genai is not None:

        try:

            client = genai.Client(api_key=api_key)

            history = []

            for item in st.session_state.messages[-10:]:

                role = (
                    "user"
                    if item["role"] == "user"
                    else "model"
                )

                history.append({
                    "role": role,
                    "parts": [{"text": item["content"]}]
                })

            result = client.models.generate_content(
                model=os.getenv(
                    "GEMINI_MODEL",
                    "gemini-2.5-flash"
                ),
                contents=history,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.4,
                },
            )

            response = result.text

        except Exception:

            response = (
                "The AI service is temporarily unavailable. "
                "You can still use the check-in and general "
                "guidance features. Please try again later."
            )

    else:

        response = local_reply(prompt)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    with st.chat_message("assistant"):
        st.markdown(response)


st.divider()

st.subheader("Find appropriate human support")

st.write(
    "If you need ongoing support, consider speaking with "
    "a qualified psychologist, psychiatrist, counsellor, doctor, "
    "or a reputable mental health organisation. "
    "For immediate danger, contact local emergency services "
    "or visit the nearest hospital."
)

st.caption(
    "Prototype status: early demonstration. Conversations are held "
    "in the app's temporary session and may be processed by the "
    "configured AI provider if an API key is added. "
    "Do not share sensitive or identifying information."
)