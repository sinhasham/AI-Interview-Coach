def generate_resume_questions(resume_text, client):

    prompt = f"""
You are an expert interviewer.

Based on this resume, generate 5 likely interview questions the candidate should prepare for:

{resume_text}

Format:
1. ...
2. ...
3. ...
4. ...
5. ...
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content