from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_policy, name='upload_policy'),
    path('register/', views.register, name='register'),
    path('chat/', views.chat_with_policy, name='chat_with_policy'),  # <-- NEW'
    path('delete/<int:file_id>/', views.delete_policy, name='delete_policy'),
]
