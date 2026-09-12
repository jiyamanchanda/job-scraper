
from fastapi import FastAPI, HTTPException, Query
from psycopg import Error
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
    role: str | None
    job_url: str
    first_seen: datetime
    last_seen: datetime
    active: bool

class AnalyticsSummary(BaseModel):
    total_jobs: int
    active_jobs: int
    remote_jobs: int
    remote_percentage: float

class AnalyticsCount(BaseModel):
    category: str
    count: int

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
    active: bool | None = Query(default=None),
    department: str | None = Query(default=None),
    location: str | None = Query(default=None),
    role: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = None,
):

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            query = """
            SELECT
            id,
            title,
            company,
            location,
            department,
            role,
            job_url,
            first_seen,
            last_seen,
            active
        FROM jobs
    """

            conditions = []
            parameters = []

            if active is not None:
                conditions.append("active = %s")
                parameters.append(active)

            if department is not None:
                conditions.append("LOWER(department) LIKE LOWER(%s)")
                parameters.append(f"%{department}%")

            if location is not None:
                conditions.append("LOWER(location) LIKE LOWER(%s)")
                parameters.append(f"%{location}%")

            if role is not None:
                conditions.append("LOWER(role) LIKE LOWER(%s)")
                parameters.append(f"%{role}%")

            if search is not None:
                conditions.append("""
                    (
                        LOWER(title) LIKE LOWER(%s)
                        OR LOWER(company) LIKE LOWER(%s)
                    )
                """)
                search_value = f"%{search}%"
                parameters.extend([search_value, search_value])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id LIMIT %s OFFSET %s"
            parameters.extend([limit, offset])

            cur.execute(query, parameters)
            rows = cur.fetchall()

            columns = [
                "id",
                "title",
                "company",
                "location",
                "department",
                "role",
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

    except Error:
        raise HTTPException(
        status_code=500,
        detail="Database error"
    )    

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
                    role,
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

    except Error:
        raise HTTPException(
        status_code=500,
        detail="Database error"
    )    

    finally:

        conn.close()

@app.get(
    "/analytics/summary",
    response_model=AnalyticsSummary
)
def analytics_summary():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    COUNT(*) AS total_jobs,
                    COUNT(*) FILTER (WHERE active = TRUE) AS active_jobs,
                    COUNT(*) FILTER (
                        WHERE active = TRUE
                        AND LOWER(location) LIKE '%remote%'
                    ) AS remote_jobs
                FROM jobs
            """)

            row = cur.fetchone()

            total_jobs = row[0]
            active_jobs = row[1]
            remote_jobs = row[2]

            remote_percentage = (
                (remote_jobs / active_jobs) * 100
                if active_jobs > 0
                else 0
            )

            return {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "remote_jobs": remote_jobs,
                "remote_percentage": round(remote_percentage, 2)
            }

    except Error:
        raise HTTPException(
        status_code=500,
        detail="Database error"
    )
    
    finally:
        conn.close()

@app.get(
    "/analytics/departments",
    response_model=list[AnalyticsCount]
)
def analytics_departments():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT department, COUNT(*) AS count
                FROM jobs
                WHERE active = TRUE
                GROUP BY department
                ORDER BY count DESC
            """)

            rows = cur.fetchall()

            return [
                {
                     "category": row[0],
                     "count": row[1]
}
                for row in rows
            ]
    except Error:
        raise HTTPException(
        status_code=500,
        detail="Database error"
    )    

    finally:
        conn.close()

@app.get(
    "/analytics/roles",
    response_model=list[AnalyticsCount]
)
def analytics_roles():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT role, COUNT(*) AS count
                FROM jobs
                WHERE active = TRUE
                GROUP BY role
                ORDER BY count DESC
            """)

            rows = cur.fetchall()

            return [
                {
                   "category": row[0],
                    "count": row[1]
}
                for row in rows
            ]
    except Error:
        raise HTTPException(
        status_code=500,
        detail="Database error"
    )    

    finally:
        conn.close()

@app.get(
    "/analytics/location-types",
    response_model=list[AnalyticsCount]
)
def analytics_location_types():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    CASE
                        WHEN LOWER(location) LIKE '%remote%'
                             AND LOWER(location) LIKE '%,%'
                            THEN 'Multiple locations'
                        WHEN LOWER(location) LIKE '%remote%'
                            THEN 'Remote'
                        ELSE 'On-site'
                    END AS location_type,
                    COUNT(*) AS count
                FROM jobs
                WHERE active = TRUE
                GROUP BY location_type
                ORDER BY count DESC
            """)

            rows = cur.fetchall()

            return [
                {
    "category": row[0],
    "count": row[1]
}
                for row in rows
            ]
    except Error:
        raise HTTPException(
        status_code=500,
        detail="Database error"
    )    

    finally:
        conn.close()

@app.get(
    "/analytics/locations",
    response_model=list[AnalyticsCount]
)
def analytics_locations():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT location, COUNT(*) AS count
                FROM jobs
                WHERE active = TRUE
                GROUP BY location
                ORDER BY count DESC
            """)

            rows = cur.fetchall()

            return [
                {
    "category": row[0],
    "count": row[1]
}
                for row in rows
            ]

    except Error:
        raise HTTPException(
        status_code=500,
        detail="Database error"
    )
        
    finally:
        conn.close()