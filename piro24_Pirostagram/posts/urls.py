from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
    path('', post_list, name='post_list'),
    path('new/', post_create, name='post_create'),
    path('story/new/', story_create, name='story_create'),
    path('like/', like_ajax, name='like_ajax'),
    path('comment/add/', comment_add_ajax, name='comment_add_ajax'),
    path('delete/<int:pk>/', post_delete, name='post_delete'),
    
    # ✅ 프로필 모달용 데이터 요청 API
    path('detail/<int:pk>/', post_detail_ajax, name='post_detail_ajax'),
]