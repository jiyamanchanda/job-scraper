import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime


URL = "https://boards.greenhouse.io/discord"


def get_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        print("Status:", response.status_code)

        return response.text

    except requests.RequestException as e:
        print("Request failed:", e)
        return None


def parse_jobs(html):
    soup = BeautifulSoup(html, "html.parser")

    jobs = soup.find_all("tr", class_="job-post")

    jobs_data = []

    for job in jobs:

        # Job title
        title_element = job.find("p", class_="body--medium")
        title = title_element.get_text(strip=True) if title_element else None

        # Location
        location_element = job.find("p", class_="body__secondary")
        location = (
            location_element.get_text(strip=True)
            if location_element
            else None
        )

        # Job URL
        link_element = job.find("a")
        job_url = link_element["href"] if link_element else None

        # Department
        department_container = job.find_parent(
            "div",
            class_="job-posts--table--department"
        )

        if department_container:
            department_element = department_container.find("h3")
            department = (
                department_element.get_text(strip=True)
                if department_element
                else None
            )
        else:
            department = None

        # Company
        company = "Discord"

        # Remove "New" if it appears in the title
        if title:
            title = title.replace("New", "").strip()

        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "department": department,
            "job_url": job_url
        }

        jobs_data.append(job_data)

    return jobs_data


def create_database(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            department TEXT,
            job_url TEXT UNIQUE,
            first_seen TEXT,
            last_seen TEXT,
            active INTEGER
        )
    """)

    conn.commit()


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


def save_jobs(conn, jobs):

    cursor = conn.cursor()

    now = datetime.now().isoformat()

    # Mark existing jobs as inactive.
    # This is only called after the scrape has passed validation.
    cursor.execute("""
        UPDATE jobs
        SET active = 0
    """)

    for job in jobs:

        cursor.execute("""
            SELECT id
            FROM jobs
            WHERE job_url = ?
        """, (job["job_url"],))

        existing_job = cursor.fetchone()

        if existing_job:

            cursor.execute("""
                UPDATE jobs
                SET title = ?,
                    company = ?,
                    location = ?,
                    department = ?,
                    last_seen = ?,
                    active = 1
                WHERE job_url = ?
            """, (
                job["title"],
                job["company"],
                job["location"],
                job["department"],
                now,
                job["job_url"]
            ))

        else:

            cursor.execute("""
                INSERT INTO jobs (
                    title,
                    company,
                    location,
                    department,
                    job_url,
                    first_seen,
                    last_seen,
                    active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job["title"],
                job["company"],
                job["location"],
                job["department"],
                job["job_url"],
                now,
                now,
                1
            ))

    conn.commit()


def find_new_jobs(conn):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, company, location, department, job_url
        FROM jobs
        WHERE first_seen = last_seen
        AND active = 1
    """)

    new_jobs = cursor.fetchall()

    if new_jobs:
        print("\nNew jobs found:")

        for job in new_jobs:
            print(
                job[0],
                "|",
                job[3],
                "|",
                job[2]
            )

    return new_jobs


def find_removed_jobs(conn):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, company, location, department, job_url
        FROM jobs
        WHERE active = 0
    """)

    removed_jobs = cursor.fetchall()

    if removed_jobs:
        print("\nRemoved jobs:")

        for job in removed_jobs:
            print(
                job[0],
                "|",
                job[3],
                "|",
                job[2]
            )

    return removed_jobs


def show_role_counts(conn):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT title
        FROM jobs
        WHERE active = 1
    """)

    jobs = cursor.fetchall()

    role_counts = {}

    for job in jobs:

        role = get_role(job[0])

        if role in role_counts:
            role_counts[role] += 1
        else:
            role_counts[role] = 1

    print("\nActive jobs by role:")

    for role, count in sorted(
        role_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(role, ":", count)


def show_department_counts(conn):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT department, COUNT(*)
        FROM jobs
        WHERE active = 1
        GROUP BY department
        ORDER BY COUNT(*) DESC
    """)

    results = cursor.fetchall()

    print("\nActive jobs by department:")

    for department, count in results:
        print(department, ":", count)


def main():

    # -------------------------
    # 1. Get page
    # -------------------------

    html = get_page(URL)

    if html is None:
        print("Scrape failed. Database was not updated.")
        return

    # -------------------------
    # 2. Parse jobs
    # -------------------------

    jobs = parse_jobs(html)

    print("Jobs scraped:", len(jobs))

    # -------------------------
    # 3. Validate scrape
    # -------------------------

    if len(jobs) < 10:
        print(
            f"WARNING: Only {len(jobs)} jobs were scraped. "
            "This may indicate a partial scrape. "
            "Database was not updated."
        )
        return

    # -------------------------
    # 4. Database
    # -------------------------

    conn = sqlite3.connect("jobs.db")

    create_database(conn)

    # -------------------------
    # 5. Save jobs
    # -------------------------

    save_jobs(conn, jobs)

    # -------------------------
    # 6. Detect changes
    # -------------------------

    find_new_jobs(conn)

    find_removed_jobs(conn)

    # -------------------------
    # 7. Analytics
    # -------------------------

    show_role_counts(conn)

    show_department_counts(conn)

    conn.close()


if __name__ == "__main__":
    main()