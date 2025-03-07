import re
import nltk
import pdfplumber
import docx
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from home.ml_utils import get_similarity  # Импортируем ML-анализ

# Загружаем необходимые данные
nltk.download("punkt")
nltk.download("stopwords")

def extract_text_from_resume(file_path):
    """Извлекает текст из резюме в формате PDF или DOCX."""
    text = ""

    if file_path.endswith(".pdf"):
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text += extracted_text + "\n"
        except Exception as e:
            print(f"❌ Ошибка при извлечении текста из PDF: {e}")

    elif file_path.endswith(".docx"):
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"❌ Ошибка при извлечении текста из DOCX: {e}")

    text = text.strip()
    if not text:
        print("⚠️ Внимание: текст из резюме не был извлечен!")

    return text

def extract_keywords(text, top_n=10):
    """Извлекает ключевые слова (навыки) из текста."""
    
    # Регулярное выражение для отбора слов с буквами и дефисами
    words = re.findall(r'\b[a-zA-Zа-яА-ЯёЁ#\+\-]+\b', text.lower())

    # Загружаем список стоп-слов
    stop_words = set(nltk.corpus.stopwords.words("russian") + nltk.corpus.stopwords.words("english"))
    words = [word for word in words if word not in stop_words]

    # Проверяем, что есть слова для анализа
    if len(words) < 3:
        return set(words)

    # Создаём TF-IDF векторизатор
    vectorizer = TfidfVectorizer(stop_words=None, max_features=top_n)
    tfidf_matrix = vectorizer.fit_transform([" ".join(words)])

    keywords = vectorizer.get_feature_names_out()
    return set(keywords)

def analyze_resume(resume_text, vacancy_text):
    """Анализируем совпадение резюме с вакансией с помощью BERT."""

    # 🔍 Анализ через ML (BERT)
    match_percentage = get_similarity(resume_text, vacancy_text)
    match_percentage = round(match_percentage, 2)  # Округляем до 2 знаков

    # 🔍 Извлекаем ключевые слова (навыки)
    resume_skills = extract_keywords(resume_text)
    vacancy_skills = extract_keywords(vacancy_text)

    # 🛠 Вычисляем совпадения навыков
    matching_skills = resume_skills.intersection(vacancy_skills)
    missing_skills = vacancy_skills - resume_skills

    # 🛠 Проверяем, что в результатах нет ошибок (разделение на буквы)
    matching_skills = {word for word in matching_skills if len(word) > 1}
    missing_skills = {word for word in missing_skills if len(word) > 1}

    print("\n🔍 Анализ навыков")
    print(f"✅ Совпадающие навыки: {', '.join(matching_skills) if matching_skills else 'Нет совпадающих навыков'}")
    print(f"⚠️ Недостающие навыки: {', '.join(missing_skills) if missing_skills else 'Все навыки совпадают'}")

    print("\n🏆 Итоговый балл (BERT):")
    print(f"🔍 Совпадение резюме с вакансией: {match_percentage}%")

    return match_percentage, matching_skills, missing_skills
