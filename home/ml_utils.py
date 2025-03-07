from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Загружаем предобученную NLP-модель
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_similarity(resume_text, vacancy_text):
    """Вычисляет схожесть между резюме и вакансией с помощью BERT."""
    resume_embedding = model.encode(resume_text)
    vacancy_embedding = model.encode(vacancy_text)

    similarity = cosine_similarity([resume_embedding], [vacancy_embedding])[0][0]
    
    return round(similarity * 100, 2)
