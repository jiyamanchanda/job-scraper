import requests
from bs4 import BeautifulSoup

url = "https://boards.greenhouse.io/discord"

response = requests.get(url)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

jobs = soup.find_all("tr", class_="job-post")

print("Number of jobs:", len(jobs))

jobs_data = []

for job in jobs:
    title_element = job.find("p", class_="body--medium")
    title = title_element.text.strip() if title_element else None

    location_element = job.find("p", class_="body__secondary")
    location = location_element.text.strip() if location_element else None

    link_element = job.find("a")
    job_url = link_element["href"] if link_element else None

    job_data = {
        "title": title,
        "location": location,
        "job_url": job_url
    }

    jobs_data.append(job_data)

print(jobs_data)