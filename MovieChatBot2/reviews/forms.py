from django import forms
from .models import Review, Genre

class ReviewForm(forms.ModelForm):
    # 장르를 체크박스 형태로 표시하며, DB의 모든 장르를 가져옵니다.
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="장르 선택 (복수 선택 가능)"
    )

    class Meta:
        model = Review
        fields = ['title', 'director', 'cast', 'genres', 'release_year', 'runtime', 'rating', 'content', 'image', 'best_scene_image']
        widgets = {
            'rating': forms.HiddenInput(), # 별점 숨김 (JS로 처리)
            'release_year': forms.NumberInput(attrs={'placeholder': '예: 2023'}),
        }