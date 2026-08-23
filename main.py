import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime


def get_page(url):
    try:
        response = requests.get(url, timeout=10)

        print("Status:", response.status_code)

        response.raise_for_status()

        return response.text

    except requests.RequestException as e:
        print("Request failed:", e)
        return None


def parse_jobs(html, company):
    soup = BeautifulSoup(html, "html.parser")

    jobs = soup.find_all("tr", class_="job-post")

    print("Number of jobs:", len(jobs))

    jobs_data = []

    for job in jobs:

        # Job title
        title_element = job.find("p", class_="body--medium")

        # Remove "New" badge
        new_badge = (
            title_element.find("span", class_="tag-container")
            if title_element
            else None
        )

        if new_badge:
            new_badge.decompose()

        title = (
            title_element.get_text(" ", strip=True)
            if title_element
            else None
        )

        # Location
        location_element = job.find("p", class_="body__secondary")

        location = (
            location_element.get_text(" ", strip=True)
            if location_element
            else None
        )

        # Job URL
        link_element = job.find("a")

        job_url = (
            link_element["href"]
            if link_element
            else None
        )

        # Department
        department_container = job.find_parent(
            "div",
            class_="job-posts--table--department"
        )

        department = (
            department_container.find("h3").get_text(" ", strip=True)
            if department_container
            else None
        )

        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "department": department,
            "job_url": job_url
        }

        jobs_data.append(job_data)

    return jobs_data

def get_role(title):

    title_lower = title.lower()

    if "software engineer" in title_lower:
        return "Software Engineering"

    elif "full-stack software engineer" in title_lower:
        return "Software Engineering"

    elif "devops" in title_lower or "qa/" in title_lower:
        return "Software Engineering"

    elif "data scientist" in title_lower:
        return "Data Science"

    elif "data engineer" in title_lower:
        return "Data Engineering"

    elif "product manager" in title_lower:
        return "Product Management"

    elif "designer" in title_lower:
        return "Design"

    elif "security" in title_lower:
        return "Security"

    elif "finance" in title_lower:
        return "Finance"

    elif "counsel" in title_lower or "legal" in title_lower:
        return "Legal"

    elif "account manager" in title_lower:
        return "Sales"

    elif "sales" in title_lower:
        return "Sales"

    elif "oracle" in title_lower or "erp" in title_lower:
        return "Business Systems"

    elif "policy" in title_lower:
        return "Policy"

    elif "threat investigator" in title_lower:
        return "Trust & Safety"

    elif "engineering manager" in title_lower:
        return "Engineering Management"

    elif "director of engineering" in title_lower:
        return "Engineering Management"

    elif "manager" in title_lower:
        return "Management"

    else:
        return "Other"

def find_new_jobs(jobs_data):

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    # Get all job URLs already in the database
    cursor.execute("""
        SELECT job_url
        FROM jobs
    """)

    existing_urls = set(row[0] for row in cursor.fetchall())

    connection.close()

    # Find jobs whose URL was not already in the database
    new_jobs = []

    for job in jobs_data:
        if job["job_url"] not in existing_urls:
            new_jobs.append(job)

    if new_jobs:
        print("\nNew jobs found:")

        for job in new_jobs:
            print(
                job["title"],
                "|",
                job["department"],
                "|",
                job["location"]
            )

def save_jobs(jobs_data):

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    # Create table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT,
        department TEXT,
        job_url TEXT UNIQUE,
        active INTEGER,
        first_seen TEXT,
        last_seen TEXT,
        role TEXT
    )
""")

    # Current time
    current_time = datetime.now().isoformat()

    # Assume every existing job is inactive
    cursor.execute("""
        UPDATE jobs
        SET active = 0
    """)

    # Process current jobs
    for job in jobs_data:

        role = get_role(job["title"])

        cursor.execute("""
    INSERT INTO jobs (
        title,
        company,
        location,
        department,
        job_url,
        active,
        first_seen,
        last_seen,
        role
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

    ON CONFLICT(job_url)
    DO UPDATE SET
        title = excluded.title,
        company = excluded.company,
        location = excluded.location,
        department = excluded.department,
        active = 1,
        last_seen = excluded.last_seen,
        role = excluded.role
""", (
    job["title"],
    job["company"],
    job["location"],
    job["department"],
    job["job_url"],
    1,
    current_time,
    current_time,
    role
))

    connection.commit()

    connection.close()

    print("Jobs saved to database.")

def check_database():

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    # Total jobs
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]

    print("Jobs in database:", count)

    # Active jobs
    cursor.execute("""
        SELECT COUNT(*)
        FROM jobs
        WHERE active = 1
    """)

    active_count = cursor.fetchone()[0]

    print("Active jobs:", active_count)

    # Inactive jobs
    cursor.execute("""
        SELECT COUNT(*)
        FROM jobs
        WHERE active = 0
    """)

    inactive_count = cursor.fetchone()[0]

    print("Inactive jobs:", inactive_count)

    # Show first 5 jobs with timestamps
    cursor.execute("""
        SELECT title, first_seen, last_seen, active
        FROM jobs
        LIMIT 5
    """)

    rows = cursor.fetchall()

    print("\nFirst 5 jobs:")

    for row in rows:
        print(row)

    connection.close()

def show_department_counts():

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT department, COUNT(*)
        FROM jobs
        WHERE active = 1
        GROUP BY department
        ORDER BY COUNT(*) DESC
    """)

    rows = cursor.fetchall()

    print("\nJobs by department:")

    for row in rows:
        print(row)

    connection.close()

def show_location_counts():

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT location, COUNT(*)
        FROM jobs
        WHERE active = 1
        GROUP BY location
        ORDER BY COUNT(*) DESC
    """)

    rows = cursor.fetchall()

    print("\nJobs by location:")

    for row in rows:
        print(row)

    connection.close()

url = "https://boards.greenhouse.io/discord"

html = get_page(url)

def show_title_counts():

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT title, COUNT(*)
        FROM jobs
        WHERE active = 1
        GROUP BY title
        ORDER BY COUNT(*) DESC
    """)

    rows = cursor.fetchall()

    print("\nJobs by title:")

    for row in rows:
        print(row)

    connection.close()

def show_role_counts():

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT role, COUNT(*)
        FROM jobs
        WHERE active = 1
        GROUP BY role
        ORDER BY COUNT(*) DESC
    """)

    rows = cursor.fetchall()

    print("\nJobs by role:")

    for row in rows:
        print(row)

    connection.close()

def show_other_jobs():

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT title, department
        FROM jobs
        WHERE active = 1
        AND role = 'Other'
    """)

    rows = cursor.fetchall()

    if rows:
        print("\nJobs classified as Other:")

        for row in rows:
            print(row)

    connection.close()

def show_new_jobs():

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT title, company, location, role
        FROM jobs
        WHERE first_seen = last_seen
        AND active = 1
    """)

    rows = cursor.fetchall()

    if rows:
        print("\nNew jobs:")

        for row in rows:
            print(row)

    connection.close()



if html:

    jobs_data = parse_jobs(html, "Discord")

    

    find_new_jobs(jobs_data)

    save_jobs(jobs_data)

    check_database()

    show_department_counts()

    show_location_counts()

    show_title_counts()

    show_role_counts()

    show_other_jobs()

    show_new_jobs()