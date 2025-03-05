import re
import nltk
import pdfplumber
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize

# Загружаем необходимые данные для nltk
nltk.download("punkt")

def extract_text_from_resume(file_path):
    """Извлекает текст из резюме в формате PDF или DOCX."""
    text = ""

    if file_path.endswith(".pdf"):
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Ошибка при извлечении текста из PDF: {e}")

    elif file_path.endswith(".docx"):
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Ошибка при извлечении текста из DOCX: {e}")

    return text.strip()

def extract_keywords(text, top_n=10):
    """Извлекает ключевые слова (навыки) из текста с помощью TF-IDF."""
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalpha()]  # Убираем числа и знаки

    vectorizer = TfidfVectorizer(stop_words="english", max_features=top_n)
    tfidf_matrix = vectorizer.fit_transform([" ".join(words)])
    
    keywords = vectorizer.get_feature_names_out()
    return set(keywords)

def extract_experience(text):
    """Извлекает количество лет опыта из текста."""
    match = re.search(r"(\d+)\s*(?:год|лет|года|years|year|месяц|месяцев|months)", text, re.IGNORECASE)
    if match:
        years = int(match.group(1))
        if "месяц" in match.group(0) or "month" in match.group(0):
            return years  # Если указано в месяцах
        return years * 12  # Если указано в годах, переводим в месяцы
    return 0  # Если не найден опыт

def analyze_resume(resume_text, vacancy_text):
    """Анализирует совпадение резюме с вакансией по навыкам и опыту работы."""

    # 1. Извлекаем ключевые слова (навыки) из резюме и вакансии
    resume_skills = extract_keywords(resume_text)
    vacancy_skills = extract_keywords(vacancy_text)

    # 2. Извлекаем опыт работы
    resume_experience = extract_experience(resume_text)
    vacancy_experience = extract_experience(vacancy_text)

    # 3. Процент совпадения по навыкам
    matching_skills = resume_skills.intersection(vacancy_skills)
    skills_score = (len(matching_skills) / max(len(vacancy_skills), 1)) * 100

    # 4. Процент совпадения по опыту работы
    experience_score = (min(resume_experience, vacancy_experience) / max(vacancy_experience, 1)) * 100

    # 5. Итоговый балл (вес навыков – 60%, опыт работы – 40%)
    final_score = (skills_score * 0.6) + (experience_score * 0.4)

    return round(final_score, 2)
