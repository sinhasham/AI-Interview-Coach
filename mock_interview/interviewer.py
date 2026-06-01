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