from datetime import datetime

from pydantic import BaseModel


class Job(BaseModel):
    title: str
    company: str
    location: str | None = None
    department: str | None = None
    job_url: str
    description: str | None = None
    source: str
    scraped_at: datetime