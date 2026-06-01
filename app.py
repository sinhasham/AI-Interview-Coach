import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

from prompts.system_prompt import SYSTEM_PROMPT

from resume.ats_scorer import calculate_ats_score
from resume.resume_reviewer import review_resume

from mock_interview.interviewer import start_mock_interview
from mock_interview.evaluator import evaluate_answer
from mock_interview.feedback import generate_feedback

from confidence.confidence_builder import motivate

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯"
)

# ==========================
# LOAD API KEY
# ==========================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ==========================
# TITLE
# ==========================

st.title("🎯 AI Interview Coach")

st.caption(
    "Practice HR, DevOps, AWS, DSA, Resume Reviews, Mock Interviews & Project Discussions"
)

# ==========================
# SIDEBAR TOOLS
# ==========================

st.sidebar.title("🚀 Interview Tools")

role = st.sidebar.selectbox(
    "Target Role",
    ["DevOps", "AWS", "SDE", "Data Analyst"]
)

resume_text = st.sidebar.text_area(
    "Paste Resume Here"
)

mock_mode = st.sidebar.checkbox(
    "Mock Interview Mode"
)

if st.sidebar.button("Boost Confidence"):
    st.sidebar.success(
        motivate()
    )

# Start Mock Interview button in sidebar — opens question in chat
if st.sidebar.button("Start Mock Interview"):
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": start_mock_interview(role)
        }
    )

if resume_text:

    ats_score = calculate_ats_score(
        resume_text
    )

    st.sidebar.success(
        f"ATS Score: {ats_score}/100"
    )

    suggestions = review_resume(
        resume_text,
        role
    )

    st.sidebar.subheader(
        "Resume Suggestions"
    )

    for item in suggestions:
        st.sidebar.write(
            f"• {item}"
        )

# ==========================
# CHAT HISTORY
# ==========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================
# USER INPUT
# ==========================

prompt = st.chat_input(
    "Ask me anything about interviews..."
)

if prompt:

    # Show user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # ==========================
    # HIDDEN EMOTION DETECTION
    # ==========================

    text = prompt.lower()

    if any(word in text for word in ["scared", "fear", "afraid"]):
        emotion = "Fear"

    elif any(word in text for word in ["nervous", "anxious", "worried"]):
        emotion = "Anxiety"

    elif any(word in text for word in ["sad", "depressed", "upset"]):
        emotion = "Sadness"

    else:
        emotion = "Neutral"

    # ==========================
    # HIDDEN CHAIN OF EMPATHY
    # ==========================

    if emotion in ["Fear", "Anxiety"]:

        empathy_chain = [
            "User is worried.",
            "User fears failure.",
            "User needs reassurance."
        ]

    elif emotion == "Sadness":

        empathy_chain = [
            "User feels discouraged.",
            "User needs motivation."
        ]

    else:

        empathy_chain = [
            "User wants interview guidance."
        ]

    # ==========================
    # HIDDEN CHAIN OF THOUGHT
    # ==========================

    reasoning_chain = [
        "Understand user query",
        "Identify interview topic",
        "Generate helpful answer",
        "Provide practical guidance"
    ]

    # DEBUG IN TERMINAL ONLY

    print("\n====================")
    print("Emotion:", emotion)
    print("Empathy Chain:", empathy_chain)
    print("Reasoning Chain:", reasoning_chain)
    print("====================\n")

    # ==========================
    # BUILD CONVERSATION
    # ==========================

    conversation = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}\n\nTarget Role: {role}"
        }
    ]

    conversation.extend(st.session_state.messages)

    # ==========================
    # LLM RESPONSE
    # ==========================

    try:

        if prompt.lower() == "start mock interview":

            bot_reply = start_mock_interview(role)

        elif prompt.lower().startswith("answer:"):

            answer = prompt.replace(
                "answer:",
                ""
            ).strip()

            bot_reply = f"""
## Evaluation

{evaluate_answer(answer)}

## Feedback

{generate_feedback()}

Type:

Start Mock Interview

to begin another round.
"""

        else:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=conversation,
                temperature=0.7,
                max_tokens=1000
            )

            bot_reply = response.choices[0].message.content

    except Exception as e:

        bot_reply = f"Error connecting to Groq API.\n\nDetails:\n{str(e)}"

    # ==========================
    # SHOW RESPONSE
    # ==========================

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": bot_reply
        }
    )