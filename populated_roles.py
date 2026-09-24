from db import get_connection
from job_utils import get_role

conn = get_connection()

try:
    with conn.cursor() as cur:
        cur.execute("SELECT id, title FROM jobs")
        rows = cur.fetchall()

        for job_id, title in rows:
            role = get_role(title)

            cur.execute(
                """
                UPDATE jobs
                SET role = %s
                WHERE id = %s
                """,
                (role, job_id)
            )

        conn.commit()

        print(f"Updated {len(rows)} jobs with roles.")

finally:
    conn.close();