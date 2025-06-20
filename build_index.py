import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


def load_employee_data(filepath='employees_data.json'):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data.get('employees', [])

def format_employee_profile(employee):
    profile = (
        f"{employee['name']} is a {employee['role']} based in {employee['location']}. "
        f"They bring {employee['experience_years']} years of experience and joined us on {employee['join_date']}. "
        f"Currently contributing to: {', '.join(employee['current_projects'])}. "
        f"Previously worked on: {', '.join(employee['past_projects'])}. "
        f"Core skills include: {', '.join(employee['skills'])}. "
        f"Certifications: {', '.join(employee.get('certifications', []))}. "
        f"Education background: {employee['education']}. "
        f"Speaks: {', '.join(employee['languages'])}. "
        f"Part of the {employee['department']} department, reporting to {employee['manager_name']}. "
        f"Current salary: ₹{employee['current_salary']} INR. "
        f"Status: {employee['employee_status']}, available from {employee['availability_date']} "
        f"({employee['availability_status']})."
    )
    return profile

def build_employee_search_index(employees):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    embeddings = []
    profile_metadata = []

    for employee in employees:
        profile_text = format_employee_profile(employee)
        embedding = model.encode(profile_text)
        embeddings.append(embedding)
        profile_metadata.append(employee)

    embedding_dim = len(embeddings[0])
    index = faiss.IndexFlatL2(embedding_dim)  # L2 distance (Euclidean)

    index.add(np.array(embeddings).astype('float32'))

    return index, profile_metadata

def save_index_and_metadata(index, metadata, index_path='employee_index.faiss', metadata_path='employee_metadata.json'):
    faiss.write_index(index, index_path)

    with open(metadata_path, 'w') as file:
        json.dump(metadata, file, indent=2)

    print(f"Index saved to: {index_path}")
    print(f"Metadata saved to: {metadata_path}")



if __name__ == "__main__":
    employee_list = load_employee_data()

    if not employee_list:
        print("No employees found in data file.")
    else:
        index, metadata = build_employee_search_index(employee_list)
        save_index_and_metadata(index, metadata)
        print("FAISS index and metadata saved successfully.")
