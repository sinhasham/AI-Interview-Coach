def evaluate_answer(answer):

    score = min(len(answer) // 20, 10)

    if score >= 8:
        return "Excellent Answer ⭐"

    elif score >= 5:
        return "Good Answer 👍"

    return "Needs More Details ⚠️"