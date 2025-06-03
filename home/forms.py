from django import forms
from .models import Vacancy, CandidateResume

class VacancyForm(forms.ModelForm):
    skills = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Введите навыки через запятую"}),
        required=False,
        label="Навыки"
    )

    class Meta:
        model = Vacancy
        fields = ["title", "description", "skills", "experience", "status"]
        labels = {
            "title": "Название вакансии",
            "description": "Описание вакансии",
            "experience": "Опыт работы (в годах)",
            "status": "Статус вакансии",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите название вакансии"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Описание вакансии"}),
            "experience": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        
    def clean_experience(self):
        years = self.cleaned_data['experience']
        return years * 12 


class ResumeForm(forms.ModelForm):
    class Meta:
        model = CandidateResume
        fields = ["vacancy", "resume"]
        labels = {
            "vacancy": "Вакансия",
            "resume": "Резюме (PDF или DOCX)"
        }
        widgets = {
            "vacancy": forms.Select(attrs={"class": "form-select"}),
            "resume": forms.FileInput(attrs={"class": "form-control"})
        }


