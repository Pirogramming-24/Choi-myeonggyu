"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from ai_app import views

urlpatterns = [
    # ✅ 회원가입 URL 추가 (가장 위나 accounts/ 위에 두세요)
    path('accounts/signup/', views.signup_view, name='signup'),

    path('admin/', admin.site.urls),
    
    # ai_app의 URL 연결
    path('', include('ai_app.urls')),
    
    # 메인 도메인(localhost:8000) 접속 시 바로 감정분석 페이지로 이동
    path('', RedirectView.as_view(url='/sentiment/', permanent=False)),
    
    # Django 기본 인증 URL (로그인/로그아웃 처리를 위해 필수)
    # /accounts/login/, /accounts/logout/ 등을 자동 생성해줌
    path('accounts/', include('django.contrib.auth.urls')),
]
