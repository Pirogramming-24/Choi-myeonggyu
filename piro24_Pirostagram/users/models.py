from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 프로필 사진 (media/profile/ 경로에 저장)
    profile_photo = models.ImageField(upload_to='profile/', blank=True, null=True)
    # 소개글
    intro = models.TextField(blank=True)
    
    # 팔로우 기능 (M2M)
    # symmetrical=False: 맞팔로우가 강제되지 않음
    followings = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='followers',
        blank=True
    )

    def __str__(self):
        return self.username
