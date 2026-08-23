import sqlite3
import pandas as pd


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


df = load_jobs()

print("Dataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

active_jobs = df[df["active"] == 1]

print("\nActive jobs:")
print(len(active_jobs))


print("\nJobs by department:")

department_counts = (
    active_jobs["department"]
    .value_counts()
)

print(department_counts)


print("\nJobs by location:")

location_counts = (
    active_jobs["location"]
    .value_counts()
)

print(location_counts.head(10))


remote_jobs = active_jobs[
    active_jobs["location"]
    .str.contains("remote", case=False, na=False)
]

print("\nRemote jobs:", len(remote_jobs))

remote_percentage = (
    len(remote_jobs) / len(active_jobs) * 100
)

print(
    f"Remote percentage: {remote_percentage:.2f}%"
)