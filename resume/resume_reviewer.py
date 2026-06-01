def review_resume(resume_text, role):

    suggestions = []

    if role.lower() == "devops":
        suggestions.extend([
            "Add Docker skills",
            "Add Kubernetes skills",
            "Add AWS projects"
        ])

    elif role.lower() == "sde":
        suggestions.extend([
            "Add DSA achievements",
            "Add GitHub links",
            "Add projects"
        ])

    return suggestions