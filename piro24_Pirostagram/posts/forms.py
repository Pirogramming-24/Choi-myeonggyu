from django import forms
from .models import Post, Story

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        # content 입력창 디자인 (선택사항)
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': '문구를 입력하세요...', 
                'style': 'width: 100%; height: 100px; border: none; resize: none; outline: none;'
            }),
        }

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['image']
        # 스토리 사진은 필수이므로 별도 위젯 설정은 선택사항