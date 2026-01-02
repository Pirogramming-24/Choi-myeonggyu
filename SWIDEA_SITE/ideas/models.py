from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# 1. 개발툴 (DevTool)
class DevTool(models.Model):
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=50)
    content = models.TextField()

    def __str__(self):
        return self.name

# 2. 아이디어 (Idea)
class Idea(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='ideas/', blank=True, null=True)
    content = models.TextField()
    interest = models.IntegerField(default=0)
    # ideas 앱의 DevTool과 연결
    devtools = models.ManyToManyField(DevTool, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 3. 찜하기 (IdeaStar)
class IdeaStar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='stars')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'idea') # 중복 찜 방지