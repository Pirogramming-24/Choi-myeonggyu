from django.db import models

class Review(models.Model):
    # 기능 1 & 4를 위한 필드들
    title = models.CharField(max_length=100)        # 영화 제목
    director = models.CharField(max_length=50)     # 감독
    cast = models.CharField(max_length=200)       # 주연
    genre = models.CharField(max_length=50)        # 장르
    release_year = models.IntegerField()           # 개봉 년도
    rating = models.IntegerField()                 # 별점 (예: 1~5)
    runtime = models.IntegerField()                # 러닝타임 (분 단위)
    content = models.TextField()                   # 리뷰 내용
    image = models.ImageField(upload_to='movie_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.genre}] {self.title}"
    
    @property
    def runtime_display(self):
        if self.runtime is None:
            return ""
        
        hours = self.runtime // 60  # 몫 (시간)
        minutes = self.runtime % 60 # 나머지 (분)
        
        if hours > 0:
            return f"{hours}시간 {minutes}분"
        else:
            return f"{minutes}분"