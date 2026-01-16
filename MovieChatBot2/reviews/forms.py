from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    # 1. 장르 선택지 목록 정의 (요청하신 목록 그대로 적용)
    GENRE_CHOICES = [
        ('액션 영화', '액션 영화'), ('모험 영화', '모험 영화'), ('예술 영화', '예술 영화'),
        ('코미디 영화', '코미디 영화'), ('다큐멘터리 영화', '다큐멘터리 영화'), ('드라마 영화', '드라마 영화'),
        ('교육 영화', '교육 영화'), ('서사 영화', '서사 영화'), ('실험 영화', '실험 영화'),
        ('엑스플로이테이션 영화', '엑스플로이테이션 영화'), ('판타지 영화', '판타지 영화'), ('누아르 영화', '누아르 영화'),
        ('공포 영화', '공포 영화'), ('멈블코어', '멈블코어'), ('뮤지컬 영화', '뮤지컬 영화'),
        ('미스터리 영화', '미스터리 영화'), ('로맨스 영화', '로맨스 영화'), ('일상물', '일상물'),
        ('애니메이션', '애니메이션'), ('드라마', '드라마'),
    ]

    # 2. genre 필드를 선택형(Select)으로 덮어쓰기
    genre = forms.ChoiceField(choices=GENRE_CHOICES, widget=forms.Select)

    class Meta:
        model = Review
        fields = [
            'title', 'director', 'cast', 'genre', 
            'release_year', 'rating', 'runtime', 'content', 'image'
        ]
        widgets = {
            'rating': forms.HiddenInput(), # 별점 숨김 (JS로 처리)
            'release_year': forms.NumberInput(attrs={'placeholder': '예: 2023'}),
        }