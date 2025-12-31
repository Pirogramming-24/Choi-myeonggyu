from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # fields 리스트에 'image'를 꼭 추가해야 합니다!
        fields = [
            'title', 'director', 'cast', 'genre', 
            'release_year', 'rating', 'runtime', 'content', 'image'
        ]
        # 별점 등을 선택형으로 바꾸고 싶다면 아래처럼 위젯을 추가할 수 있습니다.
        widgets = {
            'rating': forms.Select(choices=[(i, '★' * i) for i in range(1, 6)]),
            'release_year': forms.NumberInput(attrs={'placeholder': '예: 2023'}),
        }