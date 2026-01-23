from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 관리자 페이지에서 보고 싶은 필드 추가 설정 (선택사항)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('profile_photo', 'intro', 'followings')}),
    )