from django.contrib import admin
from .models import Vacancy, CandidateResume  # Убедись, что CandidateResume импортирован

admin.site.register(Vacancy)
admin.site.register(CandidateResume)  # Зарегистрируй модель, если её там нет
