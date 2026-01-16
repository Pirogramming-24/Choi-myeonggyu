from django.db import models

class Review(models.Model):
# 기본 정보
    title = models.CharField(max_length=100)
    director = models.CharField(max_length=50, blank=True)  # TMDB 데이터용 blank 허용
    cast = models.CharField(max_length=200, blank=True)      # TMDB 데이터용 blank 허용
    genre = models.CharField(max_length=50)
    release_year = models.IntegerField()
    rating = models.IntegerField(default=0)
    runtime = models.IntegerField(null=True, blank=True)
    content = models.TextField()
    
    # 이미지 관련 필드
    image = models.ImageField(upload_to='movie_images/', null=True, blank=True)
    best_scene_image = models.ImageField(upload_to='best_scenes/', null=True, blank=True) # 추가: 인상 깊은 장면

    # TMDB 연동 및 관리 필드
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    is_tmdb = models.BooleanField(default=False)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    tmdb_rating = models.FloatField(default=0.0) # TMDB 원본 평점 저장용

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"[{self.genre}] {self.title}"
    
    @property
    def runtime_display(self):
        if not self.runtime: return "정보 없음"
        hours = self.runtime // 60
        minutes = self.runtime % 60
        return f"{hours}시간 {minutes}분" if hours > 0 else f"{minutes}분"