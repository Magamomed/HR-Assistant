from django.urls import path
from .views import dashboard, vacancy_list, add_vacancy, edit_vacancy, delete_vacancy,  upload_resume, candidates_list, accept_candidate, reject_candidate, candidate_detail, invite_to_interview, delete_candidate

urlpatterns = [
    path('', dashboard, name='dashboard'),  # Главная страница со статистикой
    
    # Маршруты для вакансий
    path('vacancies/', vacancy_list, name='vacancy_list'),  # Список вакансий
    path('vacancies/add/', add_vacancy, name='add_vacancy'),  # Добавление вакансии
    path('vacancies/<int:pk>/edit/', edit_vacancy, name='edit_vacancy'),  # Редактирование вакансии
    path('vacancies/<int:pk>/delete/', delete_vacancy, name='delete_vacancy'), # Удаление вакансии
    path("resume/upload/", upload_resume, name="upload_resume"),
    path("candidates/", candidates_list, name="candidates_list"),
    path("candidates/<int:candidate_id>/", candidate_detail, name="candidate_detail"),
    path("candidates/<int:candidate_id>/invite/", invite_to_interview, name="invite_to_interview"),
    path("candidates/accept/<int:candidate_id>/", accept_candidate, name="accept_candidate"),
    path("candidates/reject/<int:candidate_id>/", reject_candidate, name="reject_candidate"),
    path("candidates/<int:candidate_id>/delete/", delete_candidate, name="delete_candidate"),
]
