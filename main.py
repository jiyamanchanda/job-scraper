import requests
import sqlite3
from bs4 import BeautifulSoup


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


def save_jobs(jobs_data):

    connection = sqlite3.connect("jobs.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            department TEXT,
            job_url TEXT UNIQUE
        )
    """)

    for job in jobs_data:

        cursor.execute("""
            INSERT OR IGNORE INTO jobs (
                title,
                company,
                location,
                department,
                job_url
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            job["title"],
            job["company"],
            job["location"],
            job["department"],
            job["job_url"]
        ))

    connection.commit()

    connection.close()

    print("Jobs saved to database.")
    
def check_database():

    connection = sqlite3.connect("jobs.db")

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")

    count = cursor.fetchone()[0]

    print("Jobs in database:", count)

    cursor.execute("""
        SELECT title, company, location, department
        FROM jobs
        LIMIT 5
    """)

    rows = cursor.fetchall()

    print("\nFirst 5 jobs:")

    for row in rows:
        print(row)

    connection.close()


url = "https://boards.greenhouse.io/discord"

html = get_page(url)

if html:

    jobs_data = parse_jobs(html, "Discord")

    save_jobs(jobs_data)

    check_database()