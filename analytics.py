import sqlite3
import pandas as pd
from job_utils import get_role

DB_NAME = "jobs.db"


def load_jobs():
    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT
            title,
            company,
            location,
            department,
            job_url,
            first_seen,
            last_seen,
            active
        FROM jobs
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def classify_location(location):

    if pd.isna(location):
        return "Unknown"

    location = location.lower()

    if "remote" in location:
        return "Remote"

    if " or " in location or "," in location:
        return "Multiple locations"

    return "On-site"

# --------------------------------
# Load data
# --------------------------------

df = load_jobs()


# --------------------------------
# Basic dataset information
# --------------------------------

print("Dataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())


# --------------------------------
# Active jobs
# --------------------------------

active_jobs = df[df["active"] == 1].copy()

print("\nActive jobs:")
print(len(active_jobs))


# --------------------------------
# Role classification
# --------------------------------

active_jobs["role"] = (
    active_jobs["title"]
    .apply(get_role)
)


print("\nJobs by role:")

role_counts = (
    active_jobs["role"]
    .value_counts()
)

print(role_counts)

print("\nActive jobs:")
print(len(active_jobs))


# --------------------------------
# Jobs by department
# --------------------------------

print("\nJobs by department:")

department_counts = (
    active_jobs["department"]
    .value_counts()
)

print(department_counts)


# --------------------------------
# Jobs by original location
# --------------------------------

print("\nJobs by location:")

location_counts = (
    active_jobs["location"]
    .value_counts()
)

print(location_counts)


# --------------------------------
# Classify location
# --------------------------------

active_jobs["location_type"] = (
    active_jobs["location"]
    .apply(classify_location)
)


# --------------------------------
# Jobs by location type
# --------------------------------

print("\nJobs by location type:")

location_type_counts = (
    active_jobs["location_type"]
    .value_counts()
)

print(location_type_counts)


# --------------------------------
# Location classification details
# --------------------------------

print("\nLocation classification:")

print(
    active_jobs[
        ["location", "location_type"]
    ]
    .drop_duplicates()
    .to_string(index=False)
)