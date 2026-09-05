
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from db import get_connection


app = FastAPI(
    title="Job Market Analytics API",
    description="API for the Job Market Analytics Platform",
    version="1.0.0"
)


# ----------------------------------------
# JOB RESPONSE MODEL
# ----------------------------------------

class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str | None
    department: str | None
    job_url: str
    first_seen: datetime
    last_seen: datetime
    active: bool


# ----------------------------------------
# ROOT / HEALTH CHECK
# ----------------------------------------

@app.get("/")
def root():

    return {
        "message": "Job Market Analytics API is running"
    }


# ----------------------------------------
# GET ALL JOBS / FILTER BY ACTIVE
# ----------------------------------------

@app.get("/jobs", response_model=list[Job])
def get_jobs(
    active: bool | None = Query(default=None)
):

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            if active is None:

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

            else:

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
                    WHERE active = %s
                    ORDER BY id
                    """,
                    (active,)
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


# ----------------------------------------
# GET ONE JOB
# ----------------------------------------

@app.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: int):

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
                WHERE id = %s
                """,
                (job_id,)
            )

            row = cur.fetchone()

            if row is None:

                raise HTTPException(
                    status_code=404,
                    detail="Job not found"
                )

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

            return dict(zip(columns, row))

    finally:

        conn.close()

