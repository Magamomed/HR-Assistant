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
    """Извлекает ключевые слова (навыки) из текста, убирая лишние слова."""
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalpha()]  # Убираем числа и знаки

    # Чистим список от незначащих слов (стоп-слова)
    stop_words = set(nltk.corpus.stopwords.words("russian") + nltk.corpus.stopwords.words("english"))
    words = [word for word in words if word not in stop_words]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=top_n)
    tfidf_matrix = vectorizer.fit_transform([" ".join(words)])
    
    keywords = vectorizer.get_feature_names_out()
    return set(keywords)

def extract_experience(text):
    """Извлекает количество лет или месяцев опыта работы из текста."""
    match = re.findall(r"(\d+)\s*(?:год|лет|года|years|year)", text, re.IGNORECASE)
    months_match = re.findall(r"(\d+)\s*(?:месяц|месяцев|months)", text, re.IGNORECASE)

    years = sum(map(int, match)) if match else 0
    months = sum(map(int, months_match)) if months_match else 0

    total_experience = (years * 12) + months  # Переводим года в месяцы
    return total_experience

def analyze_resume(resume_text, vacancy_text):
    """Анализирует совпадение резюме с вакансией по навыкам и опыту работы."""

    # 1. Извлекаем ключевые слова (навыки) из резюме и вакансии
    resume_skills = extract_keywords(resume_text)
    vacancy_skills = extract_keywords(vacancy_text)

    print("\n🔍 Анализ навыков")
    print(f"Извлеченные навыки из резюме: {resume_skills}")
    print(f"Навыки, требуемые вакансией: {vacancy_skills}")

    # 2. Извлекаем опыт работы
    resume_experience = extract_experience(resume_text)
    vacancy_experience = extract_experience(vacancy_text)

    print("\n🕒 Анализ опыта работы")
    print(f"Опыт кандидата (мес): {resume_experience}")
    print(f"Требуемый опыт вакансии (мес): {vacancy_experience}")

    # 3. Процент совпадения по навыкам
    matching_skills = resume_skills.intersection(vacancy_skills)
    skills_score = (len(matching_skills) / max(len(vacancy_skills), 1)) * 100

    print("\n✅ Совпадение по навыкам")
    print(f"Совпадающие навыки: {matching_skills}")
    print(f"Процент совпадения по навыкам: {skills_score:.2f}%")

    # 4. Процент совпадения по опыту работы
    experience_score = (min(resume_experience, vacancy_experience) / max(vacancy_experience, 1)) * 100

    print("\n📊 Совпадение по опыту")
    print(f"Процент совпадения по опыту: {experience_score:.2f}%")

    # 5. Итоговый балл (вес навыков – 60%, опыт работы – 40%)
    final_score = (skills_score * 0.6) + (experience_score * 0.4)

    print("\n🏆 Итоговый балл:")
    print(f"Оценка совпадения резюме с вакансией: {final_score:.2f}%")

    return round(final_score, 2)

