import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Job Market Analytics",
    page_icon="💼",
    layout="wide"
)


st.title("Job Market Analytics")
st.write("Job market dashboard powered by FastAPI and PostgreSQL.")

st.sidebar.header("Filters")

search_filter = st.sidebar.text_input(
    "Search jobs"
)

active_filter = st.sidebar.selectbox(
    "Job Status",
    ["All", "Active", "Inactive"]
)

role_filter = st.sidebar.text_input(
    "Role"
)

department_filter = st.sidebar.text_input(
    "Department"
)

location_filter = st.sidebar.text_input(
    "Location"
)

current_filters = (
    search_filter,
    active_filter,
    department_filter,
    role_filter,
    location_filter
)

if "previous_filters" not in st.session_state:
    st.session_state.previous_filters = current_filters

elif st.session_state.previous_filters != current_filters:
    st.session_state.page = 1
    st.session_state.previous_filters = current_filters

if "page" not in st.session_state:
    st.session_state.page = 1

page_size = 20
offset = (st.session_state.page - 1) * page_size

params = {}



if active_filter == "Active":
    params["active"] = "true"

elif active_filter == "Inactive":
    params["active"] = "false"

if department_filter:
    params["department"] = department_filter

if role_filter:
    params["role"] = role_filter

if location_filter:
    params["location"] = location_filter

if search_filter:
    params["search"] = search_filter

params["limit"] = page_size
params["offset"] = offset    

jobs_response = requests.get(
    f"{API_URL}/jobs",
    params=params,
    timeout=5
)


response = requests.get(
    f"{API_URL}/analytics/summary",
    timeout=5
)

if response.status_code == 200:

    data = response.json()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Jobs", data["total_jobs"])
    col2.metric("Active Jobs", data["active_jobs"])
    col3.metric("Remote Jobs", data["remote_jobs"])
    col4.metric("Remote %", f'{data["remote_percentage"]}%')

else:

    st.error("Could not connect to the FastAPI backend.")

st.divider()

st.subheader("Jobs by Role")

response = requests.get(
    f"{API_URL}/analytics/roles",
    timeout=5
)

if response.status_code == 200:
    roles = response.json()

    role_data = {
        item["category"]: item["count"]
        for item in roles
    }

    st.bar_chart(role_data)
else:
    st.error("Could not load role analytics.")

st.subheader("Jobs by Department")

response = requests.get(
    f"{API_URL}/analytics/departments",
    timeout=5
)

if response.status_code == 200:
    departments = response.json()

    department_data = {
        item["category"]: item["count"]
        for item in departments
    }

    st.bar_chart(department_data)
else:
    st.error("Could not load department analytics.")

st.subheader("Jobs by Location Type")

response = requests.get(
    f"{API_URL}/analytics/location-types",
    timeout=5
)

if response.status_code == 200:
    location_types = response.json()

    location_type_data = {
        item["category"]: item["count"]
        for item in location_types
    }

    st.bar_chart(location_type_data)
else:
    st.error("Could not load location type analytics.")

st.subheader("Jobs by Location")

response = requests.get(
    f"{API_URL}/analytics/locations",
    timeout=5
)

if response.status_code == 200:
    locations = response.json()

    location_data = {
        item["category"]: item["count"]
        for item in locations
    }

    st.bar_chart(location_data)
else:
    st.error("Could not load location analytics.")

st.divider()

st.subheader("Job Listings")

if jobs_response.status_code == 200:

    jobs = jobs_response.json()

    st.write(f"Showing {len(jobs)} jobs on page {st.session_state.page}")

    display_jobs = [
    {
        "Title": job["title"],
        "Company": job["company"],
        "Location": job["location"],
        "Department": job["department"],
        "Role": job["role"],
        "Apply": job["job_url"]
    }
    for job in jobs
]

    st.dataframe(
        display_jobs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Apply": st.column_config.LinkColumn(
                "Apply"
            )
        }
    )

    prev_col, page_col, next_col = st.columns([1, 2, 1])

    with prev_col:
        if st.button("← Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()

    with page_col:
        st.write(f"Page {st.session_state.page}")

    with next_col:
        if st.button("Next →") and len(jobs) == page_size:
            st.session_state.page += 1
            st.rerun()

else:

    st.error("Could not load job listings.")