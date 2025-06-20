from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import faiss
import json
import numpy as np
import requests
import re
from sentence_transformers import SentenceTransformer

app = FastAPI(
    title="HR Resource Chatbot API",
    version="1.0",
    description="AI-powered HR assistant using FAISS, embeddings, and Ollama"
)

# CORS middleware for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load vector index and employee metadata
index = faiss.read_index("employee_index.faiss")
with open("employee_metadata.json", "r") as f:
    metadata = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")



def embed_query(text: str):
    return model.encode([text])[0].astype("float32")

def call_ollama(prompt, model_name="mistral"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=60,
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"❌ Error contacting LLM: {e}"

def extract_top_k(query: str, default: int = 1, max_k: int = 60):
    numbers = re.findall(r"\b\d+\b", query)
    return min(int(numbers[0]), max_k) if numbers else default


class ChatRequest(BaseModel):
    query: str


class Employee(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
    location: str
    role: str
    skills: List[str]
    experience_years: int
    current_projects: List[str]
    past_projects: List[str]
    education: str
    certifications: List[str]
    languages: List[str]
    availability_status: str
    availability_date: str
    join_date: str
    current_salary: int
    department: str
    manager_name: str
    employee_status: str

@app.post("/chat")
async def chat(request: ChatRequest):
    query = request.query.strip()
    if not query or len(query) < 3:
        return {"response": "❌ Please enter a valid query so I can assist you.", "matches": []}

    if not re.fullmatch(r"[a-zA-Z0-9\s\-\.\,\?\!]+", query) or not any(char.isalpha() for char in query):
        return {
            "response": "🤖 That doesn’t look like a valid question. Try something like: *'Find React developers in Berlin'*",
            "matches": []
        }

    query_lower = query.lower()

    if "employee names" in query_lower or \
       "list employees" in query_lower or \
       ("list" in query_lower and "employees" in query_lower) or \
       ("show" in query_lower and "employees" in query_lower):

        k = extract_top_k(query_lower, default=10, max_k=len(metadata))
        names = [emp["name"] for emp in metadata[:k]]

        return {
            "response": f"Here are {len(names)} employee names:\n\n" + "\n".join(names),
            "matches": metadata[:k]
        }

    k = extract_top_k(query_lower, default=2, max_k=len(metadata))
    q_emb = embed_query(query_lower)
    D, I = index.search(np.array([q_emb]), k=k)
    top_employees = [metadata[i] for i in I[0] if i < len(metadata)]

    if not top_employees:
        return {
            "response": "😕 I couldn't find any employees matching your request. Try using different keywords or check your spelling.",
            "matches": []
        }
    contact_fields = {
        "email": "email",
        "phone": "phone_number",
        "contact": "phone_number",
        "location": "location",
        "manager": "manager_name",
        "department": "department",
        "salary": "current_salary",
        "availability": "availability_date",
        "join date": "join_date"
    }

    for emp in top_employees:
        name_lower = emp["name"].lower()
        if name_lower in query_lower or any(part in query_lower for part in name_lower.split()):
            for key, field in contact_fields.items():
                if key in query_lower:
                    return {
                        "response": f"{emp['name']}'s {key} is: {emp.get(field, 'N/A')}",
                        "matches": [emp]
                    }

    if any(key in query_lower for key in contact_fields):
        return {
            "response": "Please specify which employee you're referring to, so I can look up their contact details.",
            "matches": []
        }

    prompt = f"You are an HR assistant. The user asked:\n'{query}'\n\nHere are the top matches:\n\n"
    for emp in top_employees:
        prompt += (
            f"{emp['name']} is a {emp['role']} from {emp['location']} with {emp['experience_years']} years experience. "
            f"Skills: {', '.join(emp['skills'])}. Projects: {', '.join(emp['current_projects'] + emp['past_projects'])}. "
            f"Available from {emp['availability_date']}.\n\n"
        )
    prompt += "Respond helpfully and clearly."
    answer = call_ollama(prompt)

    return {
        "response": answer or "Sorry, I couldn't generate a response right now.",
        "matches": top_employees
    }



@app.get("/employees/search")
async def search_employees(
    skill: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_experience: Optional[int] = Query(None),
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    manager: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    certification: Optional[str] = Query(None),
    project: Optional[str] = Query(None),
    availability: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    results = []
    for emp in metadata:
        if name and name.lower() not in emp["name"].lower():
            continue
        if email and email.lower() not in emp["email"].lower():
            continue
        if skill and skill.lower() not in [s.lower() for s in emp.get("skills", [])]:
            continue
        if role and role.lower() not in emp["role"].lower():
            continue
        if location and location.lower() not in emp["location"].lower():
            continue
        if status and status.lower() != emp.get("employee_status", "").lower():
            continue
        if min_experience and emp.get("experience_years", 0) < min_experience:
            continue
        if department and department.lower() not in emp.get("department", "").lower():
            continue
        if manager and manager.lower() not in emp.get("manager_name", "").lower():
            continue
        if education and education.lower() not in emp.get("education", "").lower():
            continue
        if language and language.lower() not in [l.lower() for l in emp.get("languages", [])]:
            continue
        if certification and certification.lower() not in [c.lower() for c in emp.get("certifications", [])]:
            continue
        if availability and availability.lower() != emp.get("availability_status", "").lower():
            continue
        if project and project.lower() not in [p.lower() for p in emp.get("current_projects", []) + emp.get("past_projects", [])]:
            continue
        results.append(emp)

    start = (page - 1) * limit
    end = start + limit
    paginated = results[start:end]

    return {
        "total": len(results),
        "page": page,
        "limit": limit,
        "results": paginated
    }
