def get_role(title):

    if not title:
        return "Other"

    title_lower = title.lower()

    if "software engineer" in title_lower:
        return "Software Engineer"

    elif "data scientist" in title_lower:
        return "Data Scientist"

    elif "data engineer" in title_lower:
        return "Data Engineer"

    elif "machine learning" in title_lower:
        return "Machine Learning"

    elif "product manager" in title_lower:
        return "Product Manager"

    elif "designer" in title_lower:
        return "Designer"

    elif "security" in title_lower:
        return "Security"

    elif "devops" in title_lower:
        return "DevOps"

    elif "manager" in title_lower:
        return "Manager"

    else:
        return "Other"