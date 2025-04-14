from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Optional

from knn_model import (
    get_db_connection,
    load_features_and_ids,
    get_similar_companies,
    fetch_company,
    insert_company,
    delete_company_by_id,
    update_company_by_id,
    patch_company_by_id
)

app = FastAPI()
conn, cursor = get_db_connection()

class Company(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    funding: Optional[float] = None
    employees: Optional[int] = None
    revenue_growth: Optional[float] = None

X, company_ids, model = load_features_and_ids(cursor)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/similar")
def get_similar(company_id: int, top_k: int=3):
    return get_similar_companies(company_id, top_k, model, X, company_ids)

@app.get("/company/{id}")
def get_company(id: int):
    return fetch_company(cursor, id)

@app.post("/companies", status_code=status.HTTP_201_CREATED)
def add_company(comp: Company):
    return insert_company(cursor, conn, comp)

@app.delete("/company/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(id: int):
    return delete_company_by_id(cursor, conn, id)

@app.put("/company/{id}")
def update_company(id: int, comp: Company):
    return update_company_by_id(cursor, conn, id, comp)

@app.patch("/company/{id}")
def patch_company(id: int, comp: Company):
    return patch_company_by_id(cursor, conn, id, comp)
