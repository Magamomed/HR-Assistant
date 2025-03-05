from django.db import models

class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыта'),
        ('closed', 'Закрыта'),
    ]
    
    title = models.CharField(max_length=255, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание вакансии", blank=True, null=True)
    skills = models.CharField(max_length=500, verbose_name="Навыки", blank=True)
    experience = models.IntegerField(verbose_name="Опыт работы (в месяцах)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', verbose_name="Статус")
    created_at = models.DateField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

class CandidateResume(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="resumes/")
    match_percentage = models.FloatField(default=0)
    skills = models.TextField(blank=True, null=True)  # 🔍 Извлеченные навыки
    missing_skills = models.TextField(blank=True, null=True)  # ❌ Недостающие навыки
    status = models.CharField(
        max_length=15,
        choices=[("pending", "Ожидание"), ("interview", "На интервью"), ("accepted", "Принят"), ("rejected", "Отклонен")],
        default="pending",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Резюме на {self.vacancy.title} - {self.match_percentage}%"
