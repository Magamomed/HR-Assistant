from django.shortcuts import render

def dashboard(request):
    # Данные для отображения
    context = {
        "vacancies_open": 10,
        "resumes_uploaded": 45,
        "candidates_accepted": 7,
        "candidates_rejected": 12,
        "candidates": [
            {"name": "Ануар Акимжанов", "position": "Frontend Dev", "match": "87%", "status": "Принят", "upload_date": "03.03.2025"},
            {"name": "Айжан Ермекова", "position": "Backend Dev", "match": "75%", "status": "Отклонён", "upload_date": "02.03.2025"},
            {"name": "Ерлан Касымов", "position": "Data Scientist", "match": "80%", "status": "Не рассмотрен", "upload_date": "01.03.2025"},
        ]
    }
    return render(request, "home/dashboard.html", context)

