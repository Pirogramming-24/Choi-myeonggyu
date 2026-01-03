from django.urls import path
from . import views

app_name = 'ideas'

urlpatterns = [
    # 1. 개발툴 목록 페이지 (주소: /devtool/)
    path('devtool/', views.devtool_list, name='devtool_list'),
    # 주소: /devtool/create/ 로 들어오면 devtool_create 함수 실행
    path('devtool/create/', views.devtool_create, name='devtool_create'),
    # <int:pk>는 "여기에 정수형 숫자(id)가 들어올 거야"라는 뜻입니다.
    path('devtool/<int:pk>/', views.devtool_detail, name='devtool_detail'),
    # [추가] 삭제
    path('devtool/<int:pk>/delete/', views.devtool_delete, name='devtool_delete'),
    # [추가] 수정
    path('devtool/<int:pk>/update/', views.devtool_update, name='devtool_update'),
    # [추가] 아이디어 관련 Path
    path('', views.idea_list, name='idea_list'), # 메인 페이지 ('')
    path('create/', views.idea_create, name='idea_create'),
    path('<int:pk>/', views.idea_detail, name='idea_detail'),
    path('<int:pk>/delete/', views.idea_delete, name='idea_delete'),
    path('<int:pk>/update/', views.idea_update, name='idea_update'),
    # [추가] 관심도 조정 (action에는 'up' 또는 'down'이 들어옴)
    path('<int:pk>/interest/<str:action>/', views.idea_interest, name='idea_interest'),
    # [추가] 찜하기 토글
    path('<int:pk>/star/', views.idea_star, name='idea_star'),
]