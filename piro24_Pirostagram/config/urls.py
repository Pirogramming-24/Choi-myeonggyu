from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls')), # 메인 주소 접속 시 posts 앱으로 연결
    path('users/', include('users.urls')), # 유저 관련은 users 앱으로
]

# 미디어 파일(사진)을 조회하기 위한 설정 (개발 모드 전용)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)