from roles.devops import DEVOPS_QUESTIONS
from roles.aws import AWS_QUESTIONS
from roles.sde import SDE_QUESTIONS


def get_questions(role):

    if role == "DevOps":
        return DEVOPS_QUESTIONS

    elif role == "AWS":
        return AWS_QUESTIONS

    elif role == "SDE":
        return SDE_QUESTIONS

    return ["Tell me about yourself."]


def start_mock_interview(role):

    questions = get_questions(role)

    return f"""
🎤 Mock Interview Started

Question 1:

{questions[0]}

Reply using:

Answer: your answer
"""