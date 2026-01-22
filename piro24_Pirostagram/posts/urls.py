from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
    path('', post_list, name='post_list'),
    path('new/', post_create, name='post_create'),
    path('update/<int:pk>/', post_update, name='post_update'), # ✅ 게시글 수정
    path('story/new/', story_create, name='story_create'),
    path('like/', like_ajax, name='like_ajax'),
    path('comment/add/', comment_add_ajax, name='comment_add_ajax'),
    path('comment/delete/', comment_delete_ajax, name='comment_delete_ajax'), # ✅ 댓글 삭제
    path('comment/update/', comment_update_ajax, name='comment_update_ajax'), # ✅ 댓글 수정
    path('delete/<int:pk>/', post_delete, name='post_delete'),
    # ✅ 프로필 모달용 데이터 요청 API
    path('detail/<int:pk>/', post_detail_ajax, name='post_detail_ajax'),
    path('notification/', notification_ajax, name='notification_ajax'), 
    path('notification/read/', notification_read_ajax, name='notification_read_ajax'),
]