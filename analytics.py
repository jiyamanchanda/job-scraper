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

    location = location.strip().lower()

    # Remote jobs
    if "remote" in location:
        return "Remote"

    # Multiple locations
    if " or " in location:
        return "Multiple locations"

    # Handle comma-separated locations.
    # A simple "City, State" is still one location.
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


def analyze_roles(active_jobs):

    return (
        active_jobs["role"]
        .value_counts()
    )


def analyze_departments(active_jobs):

    return (
        active_jobs["department"]
        .value_counts()
    )


def analyze_locations(active_jobs):

    return (
        active_jobs["location"]
        .value_counts()
    )


def analyze_location_types(active_jobs):

    return (
        active_jobs["location_type"]
        .value_counts()
    )


def analyze_roles_by_department(active_jobs):

    return pd.crosstab(
        active_jobs["department"],
        active_jobs["role"]
    )

def calculate_department_percentages(active_jobs):

    department_counts = (
        active_jobs["department"]
        .value_counts()
    )

    department_percentages = (
        department_counts
        / len(active_jobs)
        * 100
    )

    return department_percentages


def generate_summary(active_jobs):

    total_jobs = len(active_jobs)

    remote_jobs = (
        active_jobs["location_type"] == "Remote"
    ).sum()

    remote_percentage = (
        remote_jobs / total_jobs * 100
    )

    top_departments = (
        active_jobs["department"]
        .value_counts()
        .head(5)
    )

    top_roles = (
        active_jobs["role"]
        .value_counts()
        .head(5)
    )

    top_locations = (
        active_jobs["location"]
        .value_counts()
        .head(5)
    )

    return {
        "total_jobs": total_jobs,
        "remote_jobs": remote_jobs,
        "remote_percentage": remote_percentage,
        "top_departments": top_departments,
        "top_roles": top_roles,
        "top_locations": top_locations
    }

def analyze_remote_by_role(active_jobs):

    role_summary = (
        active_jobs
        .groupby("role")
        .agg(
            total_jobs=("role", "size"),
            remote_jobs=("location_type", lambda x: (x == "Remote").sum())
        )
    )

    role_summary["remote_percentage"] = (
        role_summary["remote_jobs"]
        / role_summary["total_jobs"]
        * 100
    )

    return role_summary.sort_values(
        "remote_percentage",
        ascending=False
    )

def main():

    # -----------------------------
    # Load data
    # -----------------------------

    df = load_jobs()

    print("Dataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())


    # -----------------------------
    # Prepare data
    # -----------------------------

    active_jobs = prepare_data(df)

    summary = generate_summary(active_jobs)

    print("\n" + "=" * 40)
    print("JOB MARKET SUMMARY")
    print("=" * 40)

    print(f"Total active jobs: {summary['total_jobs']}")
    print(f"Remote jobs: {summary['remote_jobs']}")
    print(
        f"Remote percentage: "
        f"{summary['remote_percentage']:.2f}%"
    )

    print("\nTop 5 departments:")
    print(summary["top_departments"])

    print("\nTop 5 roles:")
    print(summary["top_roles"])

    print("\nTop 5 locations:")
    print(summary["top_locations"])

    print("\nActive jobs:")
    print(len(active_jobs))


    # -----------------------------
    # Role analysis
    # -----------------------------

    print("\nJobs by role:")

    role_counts = analyze_roles(active_jobs)

    print(role_counts)


    # -----------------------------
    # Department analysis
    # -----------------------------

    print("\nJobs by department:")

    department_counts = analyze_departments(active_jobs)

    print(department_counts)


    # -----------------------------
    # Location analysis
    # -----------------------------

    print("\nJobs by location:")

    location_counts = analyze_locations(active_jobs)

    print(location_counts)

    print("\nRemote jobs by role:")

    remote_by_role = analyze_remote_by_role(active_jobs)

    print(
    remote_by_role.round(2)
)

    # -----------------------------
    # Location type analysis
    # -----------------------------

    print("\nJobs by location type:")

    location_type_counts = analyze_location_types(active_jobs)

    print(location_type_counts)


    # -----------------------------
    # Roles by department
    # -----------------------------

    print("\nRoles by department:")

    role_department_counts = (
        analyze_roles_by_department(active_jobs)
    )

    print(role_department_counts)

    print("\nDepartment hiring percentage:")

    department_percentages = calculate_department_percentages(
    active_jobs
)

    print(department_percentages.round(2))
    # -----------------------------
    # Location classification
    # -----------------------------

    print("\nLocation classification:")

    print(
        active_jobs[
            ["location", "location_type"]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()