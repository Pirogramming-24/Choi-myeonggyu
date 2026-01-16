from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('<int:pk>/', views.review_detail, name='review_detail'),
    path('create/', views.review_create, name='review_create'),
    path('<int:pk>/update/', views.review_update, name='review_update'),
    path('<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('sync-tmdb/', views.sync_tmdb_movies, name='sync_tmdb'),
    path('chatbot/', views.chatbot_page, name='chatbot'),
    path('chatbot/api/', views.chatbot_api, name='chatbot_api'),
    path('search/', views.movie_search, name='movie_search'), # 영화 검색 페이지
    path('sync-details/<int:tmdb_id>/', views.get_tmdb_details_ajax, name='get_tmdb_details'), # 상세 정보 가져오기용
    path('delete-tmdb/', views.delete_all_tmdb, name='delete_tmdb'),
    path('init-genres/', views.init_genres, name='init_genres'),
    # [추가] 댓글 작성 경로
    path('<int:pk>/comment/', views.comment_create, name='comment_create'),
    # [수정] 인증 관련 경로
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'),
]
