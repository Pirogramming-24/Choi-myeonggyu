from django.db import models
from django.contrib.auth.models import User

class AIHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model_type = models.CharField(max_length=50)  # sentiment, summary, etc.
    input_text = models.TextField()
    result_text = models.TextField()
    image_url = models.URLField(blank=True, null=True) # 이미지 결과용
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.model_type}"