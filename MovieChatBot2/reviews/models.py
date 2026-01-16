from django.db import models

class Review(models.Model):
    title = models.CharField(max_length=100)
    director = models.CharField(max_length=50)
    cast = models.CharField(max_length=200)
    genre = models.CharField(max_length=50)
    release_year = models.IntegerField()
    rating = models.IntegerField(default=0) # 기본값 설정
    runtime = models.IntegerField(null=True, blank=True)
    content = models.TextField(blank=True) # TMDB 데이터는 리뷰 내용이 없을 수 있음
    image = models.ImageField(upload_to='movie_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- TMDB 연동을 위한 추가 필드 ---
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True) # 중복 방지
    is_tmdb = models.BooleanField(default=False) # 데이터 출처 구분
    poster_path = models.CharField(max_length=255, null=True, blank=True) # 외부 이미지 URL 저장용

    def __str__(self):
        return f"[{self.genre}] {self.title}"
    
    @property
    def runtime_display(self):
        if not self.runtime: return "정보 없음"
        hours = self.runtime // 60
        minutes = self.runtime % 60
        return f"{hours}시간 {minutes}분" if hours > 0 else f"{minutes}분"