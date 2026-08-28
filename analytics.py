import sqlite3
import pandas as pd

from job_utils import get_role

from analytics_utils import (
    get_role_counts,
    get_department_counts,
    get_location_counts,
    get_location_type_counts,
    get_remote_by_role,
    get_roles_by_department,
    get_department_percentages,
    get_department_by_location_type
)


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


def prepare_data(df):

    df = df.copy()

    # Add role classification
    df["role"] = df["title"].apply(get_role)

    # Classify location type
    df["location_type"] = df["location"].apply(classify_location)

    return df


def classify_location(location):

    if pd.isna(location):
        return "Unknown"

    location = location.strip().lower()

    # Remote jobs
    if "remote" in location:
        return "Remote"

    # Multiple possible locations
    if " or " in location:
        return "Multiple locations"

    # More than one comma usually means multiple locations
    if location.count(",") >= 2:
        return "Multiple locations"

    return "On-site"


def print_summary(active_jobs):

    print("\n" + "=" * 40)
    print("JOB MARKET SUMMARY")
    print("=" * 40)

    total_jobs = len(active_jobs)

    remote_jobs = (
        active_jobs["location_type"] == "Remote"
    ).sum()

    remote_percentage = (
        remote_jobs / total_jobs * 100
    )

    print(f"Total active jobs: {total_jobs}")
    print(f"Remote jobs: {remote_jobs}")
    print(f"Remote percentage: {remote_percentage:.2f}%")

    print("\nTop 5 departments:")
    print(
        get_department_counts(active_jobs)
        .head(5)
    )

    print("\nTop 5 roles:")
    print(
        get_role_counts(active_jobs)
        .head(5)
    )

    print("\nTop 5 locations:")
    print(
        get_location_counts(active_jobs)
        .head(5)
    )


def main():

    # Load data
    df = load_jobs()

    print("Dataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    # Prepare data
    df = prepare_data(df)

    # Only active jobs
    active_jobs = df[df["active"] == 1].copy()

    print_summary(active_jobs)

    # ----------------------------------------
    # JOBS BY ROLE
    # ----------------------------------------

    print("\nActive jobs:")
    print(len(active_jobs))

    print("\nJobs by role:")
    print(
        get_role_counts(active_jobs)
    )

    # ----------------------------------------
    # JOBS BY DEPARTMENT
    # ----------------------------------------

    print("\nJobs by department:")
    print(
        get_department_counts(active_jobs)
    )

    # ----------------------------------------
    # JOBS BY LOCATION
    # ----------------------------------------

    print("\nJobs by location:")
    print(
        get_location_counts(active_jobs)
    )

    # ----------------------------------------
    # REMOTE JOBS BY ROLE
    # ----------------------------------------

    print("\nRemote jobs by role:")
    print(
        get_remote_by_role(active_jobs)
        .sort_values(
            "remote_percentage",
            ascending=False
        )
        .round(2)
    )

    # ----------------------------------------
    # JOBS BY LOCATION TYPE
    # ----------------------------------------

    print("\nJobs by location type:")
    print(
        get_location_type_counts(active_jobs)
    )

    # ----------------------------------------
    # ROLES BY DEPARTMENT
    # ----------------------------------------

    print("\nRoles by department:")
    print(
        get_roles_by_department(active_jobs)
    )

    # ----------------------------------------
    # DEPARTMENT HIRING PERCENTAGE
    # ----------------------------------------

    print("\nDepartment hiring percentage:")
    print(
        get_department_percentages(active_jobs)
        .round(2)
    )

    # ----------------------------------------
    # DEPARTMENT × LOCATION TYPE
    # ----------------------------------------

    print("\nDepartment by location type:")
    print(
        get_department_by_location_type(active_jobs)
    )

    # ----------------------------------------
    # LOCATION CLASSIFICATION
    # ----------------------------------------

    print("\nLocation classification:")

    print(
        active_jobs[
            ["location", "location_type"]
        ]
        .drop_duplicates()
        .sort_values("location")
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()