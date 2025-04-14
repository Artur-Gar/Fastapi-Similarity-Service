import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from sklearn.neighbors import NearestNeighbors
from fastapi import HTTPException, status, Response

def get_db_connection():
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
            print("Database connection successful.")
            return conn, cursor
        except Exception as error:
            print("Database connection failed. Retrying...")
            print("Error:", error)
            time.sleep(2)


def load_features_and_ids(cursor):
    cursor.execute("SELECT company_id, funding, employees, revenue_growth FROM companies ORDER BY company_id;")
    rows = cursor.fetchall()
    dict_rows = [dict(row) for row in rows]
    company_ids = [row['company_id'] for row in dict_rows]
    X = np.array([[row['funding'], row['employees'], row['revenue_growth']] for row in dict_rows])
    k = int(np.sqrt(len(X)))
    model = NearestNeighbors(n_neighbors=k)
    model.fit(X)
    return X, company_ids, model


def get_similar_companies(company_id, top_k, model, X, company_ids):
    if company_id not in company_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Company with id {company_id} not found.")
    idx = company_ids.index(company_id)
    distances, indices = model.kneighbors([X[idx]], n_neighbors=top_k + 1)
    similar_ids = [company_ids[i] for i in indices[0] if company_ids[i] != company_id]
    return {f"Top {top_k} similar companies to ID {company_id}": similar_ids}


def fetch_company(cursor, company_id):
    cursor.execute("SELECT * FROM companies WHERE company_id = %s", (str(company_id),))
    company = cursor.fetchone()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Company with id {company_id} not found.")
    return {f"Company with id {company_id}": company}


def insert_company(cursor, conn, comp):
    query = """
    INSERT INTO companies (name, sector, country, funding, employees, revenue_growth)
    VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;
    """
    try:
        cursor.execute(query, (
            comp.name, comp.sector, comp.country,
            comp.funding, comp.employees, comp.revenue_growth
        ))
        new_company = cursor.fetchone()
        conn.commit()
        return {"company": new_company}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert company: {e}")


def delete_company_by_id(cursor, conn, company_id):
    cursor.execute("DELETE FROM companies WHERE company_id = %s RETURNING *", (str(company_id),))
    deleted = cursor.fetchone()
    if deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Company with id {company_id} not found.")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def update_company_by_id(cursor, conn, company_id, comp):
    query = """
    UPDATE companies SET name = %s, sector = %s, country = %s, funding = %s,
    employees = %s, revenue_growth = %s WHERE company_id = %s RETURNING *;
    """
    cursor.execute(query, (
        comp.name, comp.sector, comp.country, comp.funding,
        comp.employees, comp.revenue_growth, str(company_id)
    ))
    updated = cursor.fetchone()
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Company with id {company_id} not found.")
    conn.commit()
    return {"company": updated}


def patch_company_by_id(cursor, conn, company_id, comp):
    fields = comp.dict(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update.")
    set_clause = ", ".join([f"{key} = %s" for key in fields])
    values = list(fields.values())
    values.append(company_id)
    query = f"UPDATE companies SET {set_clause} WHERE company_id = %s RETURNING *;"
    cursor.execute(query, values)
    updated = cursor.fetchone()
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found.")
    conn.commit()
    return {"company": updated}
