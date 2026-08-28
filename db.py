import os
import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    connection = psycopg.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    return connection


if __name__ == "__main__":
    conn = get_connection()
    print("Database connection successful!")
    conn.close()