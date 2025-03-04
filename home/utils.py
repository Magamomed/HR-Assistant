from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
import pdfplumber

def extract_text_from_resume(file_path):
    if file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    else:
        return ""


def analyze_resume(resume_text, job_description):
    if not resume_text or not job_description:
        return 0  # Если текст не найден, совпадение 0%

    vectorizer = CountVectorizer().fit_transform([resume_text, job_description])
    vectors = vectorizer.toarray()

    similarity = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return round(similarity * 100, 2)  # Преобразуем в проценты