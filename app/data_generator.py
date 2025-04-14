import psycopg2
from psycopg2.extras import RealDictCursor
import random
import os
import time

def generate_companies(n=200):
    sectors = ['SaaS', 'Fintech', 'Healthcare', 'E-Commerce', 'AI', 'Education', 'Logistics']
    countries = ['Germany', 'France', 'Austria', 'UK', 'Spain', 'Italy', 'Netherlands']
    companies = []
    for i in range(1, n+1):
        name = f"Company_{i}"
        sector = random.choice(sectors)
        country = random.choice(countries)
        funding = round(random.uniform(1, 100), 2)
        employees = random.randint(5, 10000)
        revenue_growth = round(random.uniform(-10, 100), 2)
        companies.append((name, sector, country, funding, employees, revenue_growth))
    return companies

def connect_to_db():
#    while True:  # will try to connect until finally manage to connect
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "fastapi"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD"),
                port=os.getenv("DB_PORT", "5432"),
                cursor_factory=RealDictCursor
            )
            cursor = conn.cursor()
            print("Connected to the database")
            return conn, cursor
        except Exception as error:
            print("Failed to connect to the database:", error)
            time.sleep(2)

def main():
    conn, cursor = connect_to_db()
    companies = generate_companies(200)

    try:
        # Drop and recreate table
        cursor.execute("""
            DROP TABLE IF EXISTS companies;
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                sector TEXT,
                country TEXT,
                funding FLOAT,
                employees INTEGER,
                revenue_growth FLOAT
            );
        """)
        # Insert generated data
        insert_query = """
            INSERT INTO companies (name, sector, country, funding, employees, revenue_growth)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;
        """
        cursor.executemany(insert_query, companies)
        conn.commit()
        print(f"Table created and {len(companies)} companies inserted.")
    except Exception as e:
        conn.rollback()
        print("Error inserting data:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
