import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

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

    location = location.strip().lower()

    if "remote" in location:
        return "Remote"

    if " or " in location:
        return "Multiple locations"

    if location.count(",") >= 2:
        return "Multiple locations"

    return "On-site"


def prepare_data(df):

    active_jobs = df[df["active"] == 1].copy()

    active_jobs["role"] = (
        active_jobs["title"]
        .apply(get_role)
    )

    active_jobs["location_type"] = (
        active_jobs["location"]
        .apply(classify_location)
    )

    return active_jobs

def plot_jobs_by_role(active_jobs):

    role_counts = (
        active_jobs["role"]
        .value_counts()
        .sort_values()
    )

    plt.figure(figsize=(10, 6))

    role_counts.plot(kind="barh")

    plt.title("Active Jobs by Role")
    plt.xlabel("Number of Jobs")
    plt.ylabel("Role")

    plt.tight_layout()

    plt.savefig("charts/jobs_by_role.png")
    plt.close()

def plot_jobs_by_department(active_jobs):

    department_counts = (
        active_jobs["department"]
        .value_counts()
        .sort_values()
    )

    plt.figure(figsize=(10, 7))

    department_counts.plot(kind="barh")

    plt.title("Active Jobs by Department")
    plt.xlabel("Number of Jobs")
    plt.ylabel("Department")

    plt.tight_layout()

    

    plt.savefig("charts/jobs_by_department.png")
    plt.close()

def plot_jobs_by_location_type(active_jobs):

    location_type_counts = (
        active_jobs["location_type"]
        .value_counts()
        .sort_values()
    )

    plt.figure(figsize=(8, 5))

    location_type_counts.plot(kind="bar")

    plt.title("Jobs by Location Type")
    plt.xlabel("Location Type")
    plt.ylabel("Number of Jobs")

    plt.tight_layout()

    plt.savefig("charts/jobs_by_location_type.png")
    plt.close()


def main():

    df = load_jobs()

    active_jobs = prepare_data(df)

    plot_jobs_by_role(active_jobs)

    plot_jobs_by_department(active_jobs)

    plot_jobs_by_location_type(active_jobs)


if __name__ == "__main__":
    main()