from django.urls import path
from . import views

urlpatterns = [  
    path('', views.chat_view, name='chat'),  
    path('history/', views.history_view, name='history'),  
    path('export/', views.export_view, name='export'),  
]