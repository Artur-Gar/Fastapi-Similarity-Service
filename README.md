# 🚀 FastAPI + PostgreSQL + Docker + KNN Similarity API

This project is a full-stack containerized application for managing and analyzing company data using FastAPI, PostgreSQL, and a K-Nearest Neighbors (KNN) model for similarity search.

---

## 🗂️ Project Structure

<pre>
project/ 
├── app/
│ ├── main.py               # FastAPI app and endpoints 
│ ├── knn_model.py          # KNN loading & inference 
│ ├── data_generator.py     # (Optional) generates mock data into DB 
│ └── requirements.txt      # Python dependencies 
├── Dockerfile              # FastAPI app container 
├── docker-compose.yml      # Orchestration for API, DB, and seeder 
├── .env.example            # Environment variable template 
└── README.md
</pre>

---

## 📦 Features

- 📘 FastAPI backend with CRUD endpoints for companies
- 🧠 KNN model to find similar companies by `funding`, `employees`, and `revenue_growth`
- 🐘 PostgreSQL database in Docker
- 🧪 Optional data seeding via a separate container
- 🐳 Dockerized for easy deployment and development

---

## 🐳 Run with Docker
Start everything
```bash
docker-compose up --build
```
This will start:
- `db`: PostgreSQL database
- `seed`: Inserts 200 companies into DB
- `api`: FastAPI backend (http://localhost:8000)
---

## 🧪 API Endpoints
Use `http://localhost:8000/docs` to access Swagger UI.
- `GET /company/{id}` – Get company by ID
- `GET /similar?company_id=X&top_k=Y` – Get top K similar companies
- `POST /companies` – Add a company
- `PUT /company/{id}` – Update all fields of a company
- `PATCH /company/{id}` – Update selected fields
- `DELETE /company/{id}` – Delete a company

---

## 📝 Author

**Artur Garipov**  
[LinkedIn](https://www.linkedin.com/in/artur-garipov-36037a319) | [GitHub](https://github.com/Artur-Gar)
