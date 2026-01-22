from django.urls import path
from . import views

urlpatterns = [
    path('sentiment/', views.sentiment_view, name='sentiment'),
    path('summary/', views.summary_view, name='summary'),
    
    # ✅ 아래 줄이 없어서 에러가 난 것입니다. 추가해주세요!
    path('translation/', views.translation_view, name='translation'),
    
    path('combo/', views.combo_view, name='combo'),
]