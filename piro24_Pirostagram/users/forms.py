from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # 회원가입 시 입력받을 필드들
        fields = ('username', 'email', 'profile_photo', 'intro')