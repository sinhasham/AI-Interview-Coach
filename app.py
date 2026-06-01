import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

from prompts.system_prompt import SYSTEM_PROMPT

from resume.ats_scorer import calculate_ats_score
from resume.resume_reviewer import review_resume
from resume.pdf_parser import extract_resume_text
from resume.resume_interviewer import generate_resume_questions

from mock_interview.interviewer import start_mock_interview, get_questions
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
# RESUME PDF UPLOAD HANDLING
# ==========================

if uploaded_resume := st.session_state.get("uploaded_resume"):

    resume_text = extract_resume_text(
        uploaded_resume
    )

    analysis = generate_resume_questions(
        resume_text,
        client
    )

    st.sidebar.subheader(
        "Resume Analysis"
    )

    st.sidebar.write(
        analysis
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

uploaded_resume = st.sidebar.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

if uploaded_resume:

    resume_text = extract_resume_text(
        uploaded_resume
    )

    analysis = generate_resume_questions(
        resume_text,
        client
    )

    st.sidebar.subheader(
        "Resume Analysis"
    )

    st.sidebar.write(
        analysis
    )

resume_text_manual = st.sidebar.text_area(
    "Or Paste Resume Here"
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

    questions = get_questions(role)

    st.session_state.interview_active = True
    st.session_state.interview_questions = questions
    st.session_state.interview_index = 0
    st.session_state.interview_scores = []

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": f"""
🎤 Mock Interview Started for **{role}**

**Question 1:**

{questions[0]}
"""
        }
    )

if resume_text_manual:

    ats_score = calculate_ats_score(
        resume_text_manual
    )

    st.sidebar.success(
        f"ATS Score: {ats_score}/100"
    )

    suggestions = review_resume(
        resume_text_manual,
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

if "interview_active" not in st.session_state:
    st.session_state.interview_active = False

if "interview_index" not in st.session_state:
    st.session_state.interview_index = 0

if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = []

if "interview_scores" not in st.session_state:
    st.session_state.interview_scores = []

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

            questions = get_questions(role)

            st.session_state.interview_active = True
            st.session_state.interview_questions = questions
            st.session_state.interview_index = 0
            st.session_state.interview_scores = []

            bot_reply = f"""
🎤 Mock Interview Started for **{role}**

**Question 1:**

{questions[0]}
"""

        elif st.session_state.interview_active:

            answer = prompt

            current_index = st.session_state.interview_index
            questions = st.session_state.interview_questions
            next_index = current_index + 1

            # Ask Groq to evaluate and give correct answer
            eval_prompt = f"""
The interview question was:
{questions[current_index]}

The user answered:
{answer}

Do these 3 things:
1. Give a score out of 10 for this answer
2. Give short feedback on what was good or missing
3. Give the ideal correct answer they should have said

Format your response exactly like this:
Score: X/10
Feedback: ...
Ideal Answer: ...
"""

            eval_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": eval_prompt}],
                temperature=0.5,
                max_tokens=500
            )

            evaluation = eval_response.choices[0].message.content

            # Parse score from evaluation for scorecard
            score = 5  # default
            for line in evaluation.splitlines():
                if line.lower().startswith("score:"):
                    try:
                        score = int(line.split(":")[1].strip().split("/")[0])
                    except:
                        score = 5

            st.session_state.interview_scores.append(score)

            if next_index < len(questions):

                st.session_state.interview_index = next_index

                bot_reply = f"""
## 📊 Evaluation

{evaluation}

---

**Question {next_index + 1}:**

{questions[next_index]}
"""

            else:

                st.session_state.interview_active = False

                total = sum(st.session_state.interview_scores)
                max_score = len(questions) * 10
                percentage = int((total / max_score) * 100)

                if percentage >= 80:
                    grade = "🏆 Excellent"
                elif percentage >= 60:
                    grade = "👍 Good"
                elif percentage >= 40:
                    grade = "⚠️ Needs Improvement"
                else:
                    grade = "📚 Keep Practicing"

                bot_reply = f"""
## 📊 Evaluation

{evaluation}

---

## 🎯 Interview Complete!

| Metric | Result |
|--------|--------|
| Total Score | {total} / {max_score} |
| Percentage | {percentage}% |
| Grade | {grade} |

Type **Start Mock Interview** or click the sidebar button to try again!
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