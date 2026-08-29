from fastapi import FastAPI

from db import get_connection


app = FastAPI(
    title="Job Market Analytics API",
    description="API for the Job Market Analytics Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Job Market Analytics API is running"
    }


@app.get("/jobs")
def get_jobs():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    title,
                    company,
                    location,
                    department,
                    job_url,
                    first_seen,
                    last_seen,
                    active
                FROM jobs
                ORDER BY id
                """
            )

            rows = cur.fetchall()

            columns = [
                "id",
                "title",
                "company",
                "location",
                "department",
                "job_url",
                "first_seen",
                "last_seen",
                "active"
            ]

            jobs = [
                dict(zip(columns, row))
                for row in rows
            ]

            return jobs

    finally:
        conn.close()