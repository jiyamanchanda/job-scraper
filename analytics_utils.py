import pandas as pd



def get_role_counts(active_jobs):

    return (
        active_jobs["role"]
        .value_counts()
    )


def get_department_counts(active_jobs):

    return (
        active_jobs["department"]
        .value_counts()
    )


def get_location_counts(active_jobs):

    return (
        active_jobs["location"]
        .value_counts()
    )


def get_location_type_counts(active_jobs):

    return (
        active_jobs["location_type"]
        .value_counts()
    )


def get_remote_by_role(active_jobs):

    role_summary = (
        active_jobs
        .groupby("role")
        .agg(
            total_jobs=("role", "size"),
            remote_jobs=(
                "location_type",
                lambda x: (x == "Remote").sum()
            )
        )
    )

    role_summary["remote_percentage"] = (
        role_summary["remote_jobs"]
        / role_summary["total_jobs"]
        * 100
    )

    return role_summary


def get_roles_by_department(active_jobs):

    return pd.crosstab(
        active_jobs["department"],
        active_jobs["role"]
    )


def get_department_percentages(active_jobs):

    department_counts = get_department_counts(active_jobs)

    return (
        department_counts
        / len(active_jobs)
        * 100
    )