import re
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vacancy, CandidateResume
from .forms import VacancyForm , ResumeForm
from .utils import analyze_resume, extract_text_from_file, analyze_resume , extract_match_percent_from_text,  extract_matching_skills, extract_missing_skills, extract_name





def dashboard(request):
    """Главная страница со статистикой"""
    vacancies_open = Vacancy.objects.filter(status="open").count()
    resumes_uploaded = CandidateResume.objects.count()
    candidates_accepted = CandidateResume.objects.filter(status="accepted").count()
    candidates_rejected = CandidateResume.objects.filter(status="rejected").count()
    candidates_total = CandidateResume.objects.count()
    candidates_interview = candidates_total - candidates_accepted - candidates_rejected


    candidates = CandidateResume.objects.all().order_by("-id")

    context = {
        "vacancies_open": vacancies_open,
        "resumes_uploaded": resumes_uploaded,
        "candidates_accepted": candidates_accepted,
        "candidates_rejected": candidates_rejected,
        "candidates_interview": candidates_interview,
        "candidates": candidates
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
            vacancy.skills = request.POST.get("skills", "")  
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
        resume = form.save()

        resume_text = extract_text_from_file(resume_file)
        job_description = vacancy.description
        resume.name = extract_name(resume_text)

        if not resume.gpt_feedback:
            gpt_response = analyze_resume(resume_text, job_description)
            resume.gpt_feedback = gpt_response
            resume.match_percentage = extract_match_percent_from_text(gpt_response)
            resume.missing_skills = extract_missing_skills(gpt_response)

            required_skills = set(skill.strip().lower() for skill in vacancy.skills.split(",") if skill.strip())
            extracted_skills = set()
            resume_text_lower = resume_text.lower()

            for skill in required_skills:
                if re.search(rf'\b{re.escape(skill)}\b', resume_text_lower):
                    extracted_skills.add(skill)

            resume.skills = ", ".join(sorted(extracted_skills))
        resume.save()
        return redirect("candidates_list")

    return render(request, "home/upload_resume.html", {
        "form": form,
        "resume": resume,
        "vacancies": vacancies,
    })

    
def candidates_list(request):
    candidates = CandidateResume.objects.all()
    vacancies = Vacancy.objects.all()
    return render(request, "home/candidates_list.html", {"candidates": candidates, "vacancies": vacancies})

def candidate_detail(request, candidate_id):
    candidate = get_object_or_404(CandidateResume, id=candidate_id)
    skills = candidate.skills.split(", ") if candidate.skills else []
    missing_skills = set(candidate.missing_skills.split(", ")) if candidate.missing_skills else set()

    return render(request, "home/candidate_detail.html", {
        "candidate": candidate,
        "skills": skills,
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