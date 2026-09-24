import requests
from bs4 import BeautifulSoup
from datetime import datetime

from job_schema import Job


class GreenhouseScraper:

    def __init__(self, url, company):
        self.url = url
        self.company = company

    def get_page(self):
        try:
            response = requests.get(
                self.url,
                timeout=10
            )

            response.raise_for_status()

            print("Status:", response.status_code)

            return response.text

        except requests.RequestException as e:
            print("Request failed:", e)
            return None

    def parse_jobs(self, html):
        soup = BeautifulSoup(html, "html.parser")

        jobs = soup.find_all(
            "tr",
            class_="job-post"
        )

        jobs_data = []

        for job in jobs:

            # Job title
            title_element = job.find(
                "p",
                class_="body--medium"
            )

            title = (
                title_element.get_text(strip=True)
                if title_element
                else None
            )

            # Location
            location_element = job.find(
                "p",
                class_="body__secondary"
            )

            location = (
                location_element.get_text(strip=True)
                if location_element
                else None
            )

            # Job URL
            link_element = job.find("a")

            job_url = (
                link_element["href"]
                if link_element
                else None
            )

            # Department
            department_container = job.find_parent(
                "div",
                class_="job-posts--table--department"
            )

            if department_container:

                department_element = (
                    department_container.find("h3")
                )

                department = (
                    department_element.get_text(strip=True)
                    if department_element
                    else None
                )

            else:
                department = None

            # Remove "New" from title
            if title:
                title = title.replace(
                    "New",
                    ""
                ).strip()

            # Skip malformed jobs
            if not title or not job_url:
                continue

            job_data = Job(
                title=title,
                company=self.company,
                location=location,
                department=department,
                job_url=job_url,
                source="greenhouse",
                scraped_at=datetime.now()
            )

            jobs_data.append(
                job_data.model_dump()
            )

        return jobs_data

    def scrape(self):

        html = self.get_page()

        if html is None:
            return None

        return self.parse_jobs(html)