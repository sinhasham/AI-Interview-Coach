def calculate_ats_score(resume_text):

    score = 50

    keywords = [
        "python",
        "aws",
        "docker",
        "kubernetes",
        "git"
    ]

    for keyword in keywords:

        if keyword.lower() in resume_text.lower():
            score += 10

    return min(score, 100)