import requests
from bs4 import BeautifulSoup

url = "https://realpython.github.io/fake-jobs/"

response = requests.get(url)

print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

jobs = soup.find_all("div", class_="card-content")

jobs_data = []

for job in jobs:
    title_element = job.find("h2")
    title = title_element.text.strip() if title_element else None

    company_element = job.find("h3")
    company = company_element.text.strip() if company_element else None

    location_element = job.find("p", class_="location")
    location = location_element.text.strip() if location_element else None

    apply_link = job.find("a", string="Apply")
    job_url = apply_link["href"] if apply_link else None

    job_data = {
        "title": title,
        "company": company,
        "location": location,
        "job_url": job_url
    }

    jobs_data.append(job_data)

print(jobs_data)