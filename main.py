import requests
from bs4 import BeautifulSoup


def get_page(url):
    try:
        response = requests.get(url, timeout=10)

        print("Status:", response.status_code)

        response.raise_for_status()

        return response.text

    except requests.RequestException as e:
        print("Request failed:", e)
        return None


def parse_jobs(html):
    soup = BeautifulSoup(html, "html.parser")

    jobs = soup.find_all("tr", class_="job-post")

    print("Number of jobs:", len(jobs))

    jobs_data = []

    for job in jobs:

        # Job title
        title_element = job.find("p", class_="body--medium")
        title = title_element.text.strip() if title_element else None

        # Location
        location_element = job.find("p", class_="body__secondary")
        location = location_element.text.strip() if location_element else None

        # Job URL
        link_element = job.find("a")
        job_url = link_element["href"] if link_element else None

        # Department
        department_container = job.find_parent(
            "div",
            class_="job-posts--table--department"
        )

        department = (
            department_container.find("h3").text.strip()
            if department_container
            else None
        )

        job_data = {
            "title": title,
            "company": "Discord",
            "location": location,
            "department": department,
            "job_url": job_url
        }

        jobs_data.append(job_data)

    return jobs_data


url = "https://boards.greenhouse.io/discord"

html = get_page(url)

if html:
    jobs_data = parse_jobs(html)

    print("\nJobs data:")
    print(jobs_data)