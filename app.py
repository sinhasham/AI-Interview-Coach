import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

from prompts.system_prompt import SYSTEM_PROMPT

from resume.ats_scorer import calculate_ats_score
from resume.resume_reviewer import review_resume

from mock_interview.interviewer import start_mock_interview, get_questions
from mock_interview.evaluator import evaluate_answer
from mock_interview.feedback import generate_feedback

from confidence.confidence_builder import motivate

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="PrepIQ — AI Interview Coach",
    page_icon="🧠"
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

st.title("PrepIQ — AI Interview Coach")

st.caption(
    "From resume to offer letter · Mock Interviews · Resume Gap Analysis · ATS Scoring · Role-based Coaching"
)

st.markdown("---")

# ==========================
# SIDEBAR TOOLS
# ==========================

st.sidebar.title("🚀 Interview Tools")

role = st.sidebar.selectbox(
    "Target Role",
    ["DevOps", "AWS", "SDE", "Data Analyst"]
)

resume_text_manual = st.sidebar.text_area(
    "Paste Resume Here"
)

mock_mode = st.sidebar.checkbox(
    "Mock Interview Mode"
)

if st.sidebar.button("Boost Confidence"):
    st.sidebar.success(
        motivate()
    )

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
# CHAT HISTORY INIT
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

# Resume interview flow
if "resume_interview_active" not in st.session_state:
    st.session_state.resume_interview_active = False

if "resume_interview_index" not in st.session_state:
    st.session_state.resume_interview_index = 0

if "resume_interview_questions" not in st.session_state:
    st.session_state.resume_interview_questions = []

if "waiting_for_resume" not in st.session_state:
    st.session_state.waiting_for_resume = False

# Gap analysis flow
if "waiting_for_resume_gap" not in st.session_state:
    st.session_state.waiting_for_resume_gap = False

if "gap_job_description" not in st.session_state:
    st.session_state.gap_job_description = ""

if "gap_role" not in st.session_state:
    st.session_state.gap_role = ""

# ==========================
# WELCOME MESSAGE
# ==========================

if len(st.session_state.messages) == 0:
    welcome_message = """
👋 **Welcome to PrepIQ — AI Interview Coach!**

Everything you need to crack your next interview.

---

### 😰 Empathy Check-in
**I'm feeling anxious about my interview**
> Nervous or overwhelmed? Tell me how you're feeling and I'll help you calm down and build confidence before we begin.
> `anxiety relief` · `motivational boost` · `confidence building`

---

### 📄 Resume Interview
**review my resume**
> Paste your resume and I'll generate 5 personalised interview questions based on your actual experience.
> `tailored questions` · `experience-based`

---

### 📊 Resume Gap Analysis
**I want to apply for [role], here is the JD: …**
> Paste the job description and I'll compare it to your resume — what you have, what's missing, and exact lines to add.
> `what you have` · `what is missing` · `lines to add`

---

### 🏷️ ATS Score + Suggestions
**Give me an ATS score for my resume**
> Get a score out of 100 for how well your resume passes applicant tracking systems, with specific fixes to improve it.
> `keyword match` · `format check` · `score /100`

---

### 🎤 Mock Interview
**Start a mock interview for my role**
> I'll play the interviewer — role-based technical and behavioural questions one at a time, with feedback after each answer.
> `role-based` · `real-time feedback` · `behavioural + technical`

**Let's get started! 🚀**
"""
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": welcome_message
        }
    )

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

    reasoning_chain = [
        "Understand user query",
        "Identify interview topic",
        "Generate helpful answer",
        "Provide practical guidance"
    ]

    print("\n====================")
    print("Emotion:", emotion)
    print("Empathy Chain:", empathy_chain)
    print("Reasoning Chain:", reasoning_chain)
    print("====================\n")

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

        # ==========================
        # FLOW 2 — GAP ANALYSIS TRIGGER
        # ==========================

        if any(phrase in prompt.lower() for phrase in [
            "i want to apply",
            "want to apply for",
            "applying for",
            "job description",
            "here is the job",
            "here is jd",
            "this is the jd",
            "this is the job description"
        ]):

            st.session_state.waiting_for_resume_gap = True
            st.session_state.gap_job_description = prompt

            detected_role = role
            for r in ["devops", "aws", "sde", "data analyst", "backend", "frontend", "fullstack"]:
                if r in prompt.lower():
                    detected_role = r.title()
                    break

            st.session_state.gap_role = detected_role

            bot_reply = f"""
📋 **Job Description received for {detected_role} role!**

Now please **paste your resume** below and I will compare it against this JD and tell you:

✅ What you already have  
❌ What is missing  
📝 Exact lines to add to get selected
"""

        # ==========================
        # FLOW 2 — USER PASTES RESUME FOR GAP ANALYSIS
        # ==========================

        elif st.session_state.waiting_for_resume_gap:

            st.session_state.waiting_for_resume_gap = False

            user_resume = prompt
            jd = st.session_state.gap_job_description
            target_role = st.session_state.gap_role

            gap_prompt = f"""
You are an expert ATS resume coach and career advisor.

The candidate wants to apply for: {target_role}

Job Description:
{jd}

Candidate Resume:
{user_resume}

Analyze the resume against the job description and give a detailed report in this exact format:

## ✅ What You Already Have
List the skills, experience, and keywords from the JD that are already present in the resume.

## ❌ What Is Missing
List the skills, tools, certifications, or experience mentioned in the JD that are NOT in the resume.

## 📝 Lines to Add to Your Resume
Write exact bullet points the candidate should add to their resume to match the JD and pass ATS screening. Make them professional and impactful.

## 🎯 Overall Match Score
Give a score like: Your resume matches X% of this job description.
"""

            gap_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": gap_prompt}],
                temperature=0.5,
                max_tokens=1000
            )

            bot_reply = gap_response.choices[0].message.content

        # ==========================
        # FLOW 1 — RESUME INTERVIEW TRIGGER
        # ==========================

        elif any(word in prompt.lower() for word in [
            "resume interview",
            "interview from resume",
            "questions from resume",
            "review my resume",
            "resume based",
            "based on my resume"
        ]):

            st.session_state.waiting_for_resume = True
            st.session_state.resume_interview_active = False

            bot_reply = """
📄 **Resume Interview Mode**

Please **paste your resume text** below and I will generate 5 personalized interview questions based on your experience and skills.
"""

        # ==========================
        # FLOW 1 — USER PASTES RESUME FOR INTERVIEW
        # ==========================

        elif st.session_state.waiting_for_resume:

            st.session_state.waiting_for_resume = False

            resume_text = prompt

            resume_prompt = f"""
You are an expert technical interviewer.

Based on the following resume, generate exactly 5 interview questions that are specific to this candidate's experience, skills, and projects.

Resume:
{resume_text}

Format exactly like this:
1. ...
2. ...
3. ...
4. ...
5. ...

Only output the 5 questions. Nothing else.
"""

            resume_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": resume_prompt}],
                temperature=0.7,
                max_tokens=500
            )

            questions_text = resume_response.choices[0].message.content

            questions = []
            for line in questions_text.strip().splitlines():
                line = line.strip()
                if line and line[0].isdigit():
                    question = line.split(".", 1)[-1].strip()
                    questions.append(question)

            if not questions:
                questions = ["Tell me about yourself and your experience."]

            st.session_state.resume_interview_active = True
            st.session_state.resume_interview_questions = questions
            st.session_state.resume_interview_index = 0
            st.session_state.interview_scores = []

            bot_reply = f"""
✅ **Resume received! Starting your personalized interview.**

---

**Question 1:**

{questions[0]}
"""

        # ==========================
        # FLOW 1 — RESUME INTERVIEW IN PROGRESS
        # ==========================

        elif st.session_state.resume_interview_active:

            answer = prompt
            current_index = st.session_state.resume_interview_index
            questions = st.session_state.resume_interview_questions
            next_index = current_index + 1

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

            score = 5
            for line in evaluation.splitlines():
                if line.lower().startswith("score:"):
                    try:
                        score = int(line.split(":")[1].strip().split("/")[0])
                    except:
                        score = 5

            st.session_state.interview_scores.append(score)

            if next_index < len(questions):

                st.session_state.resume_interview_index = next_index

                bot_reply = f"""
## 📊 Evaluation

{evaluation}

---

**Question {next_index + 1}:**

{questions[next_index]}
"""

            else:

                st.session_state.resume_interview_active = False

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

## 🎯 Resume Interview Complete!

| Metric | Result |
|--------|--------|
| Total Score | {total} / {max_score} |
| Percentage | {percentage}% |
| Grade | {grade} |

Type **review my resume** to start again!
"""

        # ==========================
        # MOCK INTERVIEW TRIGGER
        # ==========================

        elif prompt.lower() == "start mock interview":

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

        # ==========================
        # MOCK INTERVIEW IN PROGRESS
        # ==========================

        elif st.session_state.interview_active:

            answer = prompt
            current_index = st.session_state.interview_index
            questions = st.session_state.interview_questions
            next_index = current_index + 1

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

            score = 5
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

        # ==========================
        # NORMAL CHAT
        # ==========================

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

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": bot_reply
        }
    )