from django.shortcuts import render, redirect, get_object_or_404
from .models import Vacancy, CandidateResume
from .forms import VacancyForm , ResumeForm
from .utils import analyze_resume, extract_text_from_resume

def dashboard(request):
    """Главная страница со статистикой"""
    context = {
        "vacancies_open": Vacancy.objects.filter(status="open").count(),
        "resumes_uploaded": 45,  # Пока статичное число
        "candidates_accepted": 7,
        "candidates_rejected": 12,
        "candidates": [
            {"name": "Ануар Акимжанов", "position": "Frontend Dev", "match": "87%", "status": "Принят", "upload_date": "03.03.2025"},
            {"name": "Айжан Ермекова", "position": "Backend Dev", "match": "75%", "status": "Отклонён", "upload_date": "02.03.2025"},
            {"name": "Ерлан Касымов", "position": "Data Scientist", "match": "80%", "status": "Не рассмотрен", "upload_date": "01.03.2025"},
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



def upload_resume(request):
    form = ResumeForm(request.POST or None, request.FILES or None)
    resume = None 
    vacancies = Vacancy.objects.all()

    if form.is_valid():
        vacancy = form.cleaned_data['vacancy']
        resume_file = form.cleaned_data['resume']

        # Удаляем старые резюме для этой вакансии
        CandidateResume.objects.filter(vacancy=vacancy).delete()

        # Создаём новое резюме
        resume = form.save()

        # 🔍 Проверяем, читается ли текст резюме
        resume_text = extract_text_from_resume(resume.resume.path)
        print(f"📄 Извлеченный текст из резюме:\n{resume_text}")

        # 🔍 Проверяем описание вакансии
        print(f"📋 Описание вакансии:\n{vacancy.description}")

        # Анализируем совпадение
        match_percentage = analyze_resume(resume_text, vacancy.description)
        print(f"✅ Совпадение: {match_percentage}%")

        # Сохраняем процент совпадения
        resume.match_percentage = match_percentage
        resume.save()

        return redirect("candidates_list")
    
    return render(request, "home/upload_resume.html", {"form": form, "resume": resume, "vacancies": vacancies})


def candidates_list(request):
    candidates = CandidateResume.objects.all()
    return render(request, "home/candidates.html", {"candidates": candidates})

def accept_candidate(request, candidate_id):
    candidate = get_object_or_404(CandidateResume, id=candidate_id)
    candidate.status = "accepted"
    candidate.save()
    return redirect("candidates_list")

def reject_candidate(request, candidate_id):
    candidate = get_object_or_404(CandidateResume, id=candidate_id)
    candidate.status = "rejected"
    candidate.save()
    return redirect("candidates_list")