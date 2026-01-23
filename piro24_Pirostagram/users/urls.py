from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    
    path('search/', search_view, name='search'),
    path('follow/<int:user_id>/', follow_ajax, name='follow_ajax'),
    path('<int:user_id>/list/<str:kind>/', follow_list_view, name='follow_list'),
    
    # ✅ 중요: 알림 페이지가 프로필보다 '반드시' 위에 있어야 합니다!
    path('notifications/', notification_view, name='notifications'), 

    # ⛔️ 이 줄은 무조건 가장 마지막에 있어야 합니다.
    # (다른 모든 단어를 유저 아이디로 인식하기 때문)
    path('<str:username>/', profile_view, name='profile'),
]