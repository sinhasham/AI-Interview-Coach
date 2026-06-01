def generate_feedback(answer):

    feedback = []

    if len(answer) < 50:
        feedback.append(
            "Try explaining in more detail."
        )

    if len(answer) > 100:
        feedback.append(
            "Good level of explanation."
        )

    if not feedback:
        feedback.append(
            "Keep practicing."
        )

    return "\n".join(feedback)