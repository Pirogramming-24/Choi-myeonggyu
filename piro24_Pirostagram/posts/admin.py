from django.contrib import admin
from .models import Post, PostImage, Comment, Story, StoryImage # PostImage 추가

# 인라인 기능을 사용해 Story 생성 시 StoryImage를 한 번에 올리도록 설정
class StoryImageInline(admin.TabularInline):
    model = StoryImage
    extra = 3  # 기본으로 보여줄 이미지 업로드 칸 수

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    inlines = [StoryImageInline]

# ✅ PostImage를 게시글 작성 화면 안에 넣기 위한 설정
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 3  # 기본으로 빈 사진 업로드 칸을 3개 보여줌

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content', 'created_at']
    list_display_links = ['id', 'content']
    inlines = [PostImageInline]  # <-- 여기에 Inline 추가