

from job_utils import get_role
from db import get_connection
from job_schema import Job
from scrapers.greenhouse import GreenhouseScraper
from datetime import datetime


URL = "https://boards.greenhouse.io/discord"








def get_active_job_urls(conn):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT job_url
        FROM jobs
        WHERE active = TRUE
    """)

    return {row[0] for row in cursor.fetchall()}


def save_jobs(conn, jobs, previous_active_urls):

    cursor = conn.cursor()

    now = datetime.now()

    current_job_urls = {
        job["job_url"]
        for job in jobs
        if job["job_url"]
    }

    removed_urls = previous_active_urls - current_job_urls

    # Mark all existing jobs as inactive first
    cursor.execute("""
        UPDATE jobs
        SET active = FALSE
    """)

    for job in jobs:

        cursor.execute("""
            SELECT id
            FROM jobs
            WHERE job_url = %s
        """, (job["job_url"],))

        existing_job = cursor.fetchone()

        if existing_job:

            cursor.execute("""
                UPDATE jobs
                SET title = %s,
                    company = %s,
                    location = %s,
                    department = %s,
                    role = %s,
                    last_seen = %s,
                    active = TRUE
                WHERE job_url = %s
            """, (
                job["title"],
                job["company"],
                job["location"],
                job["department"],
                get_role(job["title"]),
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
                    role,
                    job_url,
                    first_seen,
                    last_seen,
                    active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                job["title"],
                job["company"],
                job["location"],
                job["department"],
                get_role(job["title"]),
                job["job_url"],
                now,
                now,
                True
            ))

    conn.commit()

    return removed_urls


def find_new_jobs(conn):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, company, location, department, job_url
        FROM jobs
        WHERE first_seen = last_seen
        AND active = TRUE
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


def find_removed_jobs(conn, removed_urls):

    if not removed_urls:
        return

    cursor = conn.cursor()

    print("\nRemoved jobs:")

    for job_url in removed_urls:

        cursor.execute("""
            SELECT title, company, location, department
            FROM jobs
            WHERE job_url = %s
        """, (job_url,))

        job = cursor.fetchone()

        if job:
            print(
                job[0],
                "|",
                job[3],
                "|",
                job[2]
            )


def show_role_counts(conn):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT title
        FROM jobs
        WHERE active = TRUE
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
        WHERE active = TRUE
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

    scraper = GreenhouseScraper(
    URL,
    "Discord"
)

    jobs = scraper.scrape()

    if jobs is None:
        print("Scrape failed. Database was not updated.")
        return

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

    conn = get_connection()

    previous_active_urls = get_active_job_urls(conn)

    removed_urls = save_jobs(
        conn,
        jobs,
        previous_active_urls
    )

    find_new_jobs(conn)

    find_removed_jobs(conn, removed_urls)

    # -------------------------
    # 7. Analytics
    # -------------------------

    show_role_counts(conn)

    show_department_counts(conn)

    conn.close()


if __name__ == "__main__":
    main()