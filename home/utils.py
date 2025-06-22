import os
import re
import pdfplumber
import docx
import requests
from dotenv import load_dotenv

load_dotenv()


def extract_text_from_file(file):
    text = ""

    try:
        if file.name.endswith(".pdf"):
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        elif file.name.endswith(".docx"):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"Ошибка при извлечении текста: {e}")

    return text.strip()


def analyze_resume(resume_text, job_description):
    prompt = f"""
Ты профессиональный HR-ассистент. Ниже предоставлены резюме и описание вакансии.

📄 Резюме:
\"\"\"{resume_text}\"\"\"

📋 Вакансия:
\"\"\"{job_description}\"\"\"

🔍 Твоя задача:
- Проанализируй совпадение навыков.
- Не завышай процент, если навыков мало.
- Если совпадают меньше 3 навыков — процент должен быть не выше 40%.
- Если совпадают 3-4 навыка — процент не должен быть выше 60%.
- Только при почти полном совпадении ставь больше 80%.
- Будь строгим: если кандидат backend-разработчик, а вакансия frontend — процент должен быть низким.

🔎 Верни строго в формате:
Процент совпадения: XX%
Недостающие навыки: ...
Решение: ...
"""

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"

    data = {
        "messages": [
            {"role": "system", "content": "Ты строгий и честный HR-аналитик. Не преувеличивай соответствие кандидатов."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "top_p": 1.0,
        "max_tokens": 700
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ошибка GPT (Azure): {e}"


def extract_match_percent_from_text(text):
    match = re.search(r"(\d{1,3})\s?%", text)
    return float(match.group(1)) if match else 0.0

def extract_matching_skills(text):
    match = re.search(r"Навыки[:\-]?\s*(.+?)\n", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_missing_skills(text):
    match = re.search(r"Недостающие навыки[:\-]?\s*(.+?)(\n|Решение:|$)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_name(text):
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if line and len(line.split()) >= 2 and not any(x in line.lower() for x in ["резюме", "@", "email", "телефон", "github", "linkedin"]):
            return line
    return "Неизвестный кандидат"
