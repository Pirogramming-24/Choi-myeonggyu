from django.db import models
from config import settings # settings.AUTH_USER_MODEL 참조 권장
from uuid import uuid4
from django.utils import timezone
import os

# ✅ 파일명 변경 및 경로 설정 함수 (여기 추가!)
def uuid_name_upload_to(instance, filename):
    # 파일의 확장자(jpg, png 등) 추출
    ext = filename.split('.')[-1]
    
    # 파일명을 랜덤한 32글자(uuid) + 확장자로 변경 (예: a1b2c3d4....jpg)
    uuid_name = uuid4().hex
    filename = f'{uuid_name}.{ext}'
    
    # 저장 경로: media/posts/2024/01/22/랜덤파일명.jpg 형태로 저장
    return os.path.join('posts', timezone.now().strftime('%Y/%m/%d'), filename)

# 1. 게시글 모델
class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    # 게시글 사진 (여러 장일 경우 별도 모델로 분리하지만, 일단 1장 기준으로 뼈대 잡음. 필요 시 확장)
    # image = models.ImageField(upload_to='posts/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 좋아요 기능 (M2M)
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='liked_posts', 
        blank=True
    )

    def __str__(self):
        return f"{self.author.username}의 게시글 - {self.pk}"
    pass
    
# ✅ 새로 추가할 모델 (사진 여러 장 저장을 위함)
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    
    # ✅ upload_to에 방금 만든 함수를 연결합니다.
    photo = models.ImageField(upload_to=uuid_name_upload_to)

    def __str__(self):
        return f"Image for post {self.post.pk}"

# 2. 댓글 모델
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=200) # 댓글은 보통 짧으므로 CharField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 챌린지: 대댓글을 위한 필드 (자기 자신 참조)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )

class Story(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(upload_to='stories/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 24시간 지났는지 확인하는 메서드 (선택사항)
    def is_expired(self):
        from datetime import timedelta
        from django.utils import timezone
        return timezone.now() > self.created_at + timedelta(hours=24)

# 4. 스토리 이미지 모델 (실제 사진들)
class StoryImage(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='stories/') 

class Notification(models.Model):
    TYPE_CHOICES = (
        ('post', '새 게시글'),
        ('follow', '팔로우'),
        ('like', '좋아요'), # (선택사항)
    )
    
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False) # 읽음 여부
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} : {self.message}"