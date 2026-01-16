from django.db import models
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    # [추가] 작성자 필드: 유저가 삭제되면 해당 유저의 리뷰도 삭제되도록 설정(CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    title = models.CharField(max_length=100)
    director = models.CharField(max_length=100, blank=True)
    cast = models.CharField(max_length=255, blank=True)
    genres = models.ManyToManyField(Genre, related_name='reviews') 
    release_year = models.IntegerField()
    rating = models.IntegerField(default=0)
    runtime = models.IntegerField(null=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='movie_images/', null=True, blank=True)
    best_scene_image = models.ImageField(upload_to='best_scenes/', null=True, blank=True)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    is_tmdb = models.BooleanField(default=False)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def runtime_display(self):
        if not self.runtime: return "정보 없음"
        h, m = divmod(self.runtime, 60)
        return f"{h}시간 {m}분" if h > 0 else f"{m}분"
    
class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}의 댓글: {self.content[:20]}"