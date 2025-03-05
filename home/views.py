from django.shortcuts import render, redirect, get_object_or_404
from .models import Vacancy, CandidateResume
from .forms import VacancyForm , ResumeForm
from .utils import analyze_resume, extract_text_from_resume , extract_keywords





def dashboard(request):
    """Главная страница со статистикой"""
    vacancies_open = Vacancy.objects.filter(status="open").count()
    resumes_uploaded = CandidateResume.objects.count()  # Подсчет загруженных резюме
    candidates_accepted = CandidateResume.objects.filter(status="accepted").count()
    candidates_rejected = CandidateResume.objects.filter(status="rejected").count()

    candidates = CandidateResume.objects.all().order_by("-id")  # Последние загруженные резюме

    context = {
        "vacancies_open": vacancies_open,
        "resumes_uploaded": resumes_uploaded,
        "candidates_accepted": candidates_accepted,
        "candidates_rejected": candidates_rejected,
        "candidates": [
            {
                "name": "Неизвестный кандидат" if not candidate.resume else candidate.resume.name,
                "position": candidate.vacancy.title,
                "match": f"{candidate.match_percentage}%",
                "status": "Принят" if candidate.status == "accepted" else "Отклонён" if candidate.status == "rejected" else "Не рассмотрен",
                "upload_date": candidate.resume.uploaded_at.strftime("%d.%m.%Y") if hasattr(candidate.resume, "uploaded_at") else "Неизвестно"
            }
            for candidate in candidates
        ]
    }
    return render(request, "home/dashboard.html", context)

def vacancy_list(request):
    """Страница со списком вакансий"""
    status_filter = request.GET.get("status", "all")

    if status_filter == "open":
        vacancies = Vacancy.objects.filter(status="open")
    elif status_filter == "closed":
        vacancies = Vacancy.objects.filter(status="closed")
    else:
        vacancies = Vacancy.objects.all()

    return render(request, "home/vacancy_list.html", {"vacancies": vacancies})


def add_vacancy(request):
    """Добавление новой вакансии"""
    if request.method == "POST":
        form = VacancyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("vacancy_list")
    else:
        form = VacancyForm()

    return render(request, "home/add_vacancy.html", {"form": form})


def edit_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    if request.method == "POST":
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.skills = request.POST.get("skills", "")  # Сохраняем навыки как строку через запятую
            vacancy.save()
            return redirect("vacancy_list")
    else:
        form = VacancyForm(instance=vacancy)

    return render(request, "home/add_vacancy.html", {"form": form, "vacancy": vacancy})


def delete_vacancy(request, pk):
    """Удаление вакансии"""
    vacancy = get_object_or_404(Vacancy, pk=pk)
    vacancy.delete()
    return redirect("vacancy_list")


from django.shortcuts import render, redirect
from .forms import ResumeForm
from .models import CandidateResume, Vacancy
from .utils import analyze_resume, extract_text_from_resume

def upload_resume(request):
    form = ResumeForm(request.POST or None, request.FILES or None)
    resume = None 
    vacancies = Vacancy.objects.all()

    if form.is_valid():
        vacancy = form.cleaned_data['vacancy']
        resume_file = form.cleaned_data['resume']

        # Удаляем старое резюме кандидата для этой вакансии
        CandidateResume.objects.filter(vacancy=vacancy).delete()

        # Создаём новое резюме
        resume = form.save()

        # 🔍 Извлекаем текст из резюме
        resume_text = extract_text_from_resume(resume.resume.path)
        print(f"📄 Извлеченный текст из резюме:\n{resume_text}")

        # 🔍 Проверяем описание вакансии
        print(f"📋 Описание вакансии:\n{vacancy.description}")

        # 🔍 Извлекаем навыки из резюме и вакансии
        candidate_skills = extract_keywords(resume_text)
        vacancy_skills = extract_keywords(vacancy.description)

        # 🛠 Вычисляем совпадения навыков
        matching_skills = candidate_skills.intersection(vacancy_skills)
        missing_skills = vacancy_skills - candidate_skills

        # 💾 Сохраняем навыки кандидата
        resume.skills = ", ".join(candidate_skills)
        resume.missing_skills = ", ".join(missing_skills)
        resume.save()

        # 🔍 Анализируем процент совпадения
        match_percentage = analyze_resume(resume_text, vacancy.description)
        print(f"✅ Совпадение: {match_percentage}%")

        # 💾 Сохраняем процент совпадения
        resume.match_percentage = match_percentage
        resume.save()

        return redirect("candidates_list")

    return render(request, "home/upload_resume.html", {"form": form, "resume": resume, "vacancies": vacancies})


def candidates_list(request):
    candidates = CandidateResume.objects.all()
    vacancies = Vacancy.objects.all()
    return render(request, "home/candidates_list.html", {"candidates": candidates, "vacancies": vacancies})

def candidate_detail(request, candidate_id):
    candidate = get_object_or_404(CandidateResume, id=candidate_id)

    # Проверяем, есть ли сохранённые навыки
    candidate_skills = set(candidate.skills.split(", ")) if candidate.skills else set()
    missing_skills = set(candidate.missing_skills.split(", ")) if candidate.missing_skills else set()

    return render(request, "home/candidate_detail.html", {
        "candidate": candidate,
        "matching_skills": candidate_skills,
        "missing_skills": missing_skills,
    })

def invite_to_interview(request, candidate_id):
    candidate = get_object_or_404(CandidateResume, id=candidate_id)
    candidate.status = "interview"
    candidate.save()
    return redirect("candidates_list")

def accept_candidate(request, candidate_id):
    candidate = get_object_or_404(CandidateResume, id=candidate_id)
    candidate.status = "accepted"
    candidate.save()
    return redirect("dashboard")

def reject_candidate(request, candidate_id):
    candidate = get_object_or_404(CandidateResume, id=candidate_id)
    candidate.status = "rejected"
    candidate.save()
    return redirect("dashboard")

def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(CandidateResume, id=candidate_id)
    candidate.delete()
    return redirect("candidates_list")