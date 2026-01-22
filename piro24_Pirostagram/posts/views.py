import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder
from .models import Post, Comment, Story, PostImage
from .forms import PostForm, StoryForm

# 1. 메인 피드
def post_list(request):
    posts = Post.objects.all().order_by('-created_at').prefetch_related(
        'images', 'comments', 'comments__author', 'comments__replies', 'comments__replies__author'
    )
    
    # 24시간 내 스토리 가져오기
    one_day_ago = timezone.now() - timedelta(hours=24)
    active_stories = Story.objects.filter(created_at__gte=one_day_ago).select_related('author').order_by('created_at')
    
    # ✅ [추가] 내가 올린 스토리가 있는지 확인
    user_has_story = False
    if request.user.is_authenticated:
        user_has_story = active_stories.filter(author=request.user).exists()

    # JSON 데이터 생성 (기존 로직 유지)
    story_dict = {}
    for story in active_stories:
        uid = story.author.id
        if uid not in story_dict:
            story_dict[uid] = {
                'username': story.author.username,
                'profile_image': story.author.profile_photo.url if story.author.profile_photo else None,
                'items': []
            }
        story_dict[uid]['items'].append(story.image.url)

    story_json = json.dumps(story_dict, cls=DjangoJSONEncoder)

    ctx = {
        'posts': posts,
        'story_json': story_json,
        'story_authors': story_dict.values(),
        'user_has_story': user_has_story, # ✅ 템플릿으로 전달
    }
    return render(request, 'posts/post_list.html', ctx)

# 2. 스토리 업로드 (멀티 파일 지원)
@login_required
def story_create(request):
    if request.method == 'POST':
        images = request.FILES.getlist('photos')
        if images:
            for image in images:
                Story.objects.create(author=request.user, image=image)
            return redirect('posts:post_list')
    return render(request, 'posts/story_create.html')

# 3. [New] 게시글 상세 데이터 반환 (프로필 모달용 AJAX)
def post_detail_ajax(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 이미지 URL 리스트
    images = [img.photo.url for img in post.images.all()]
    
    # 댓글 리스트 (대댓글 포함 구조화)
    comments_data = []
    for comment in post.comments.filter(parent=None).order_by('created_at'):
        replies = []
        for reply in comment.replies.all().order_by('created_at'):
            replies.append({
                'id': reply.id,
                'username': reply.author.username,
                'content': reply.content,
            })
        comments_data.append({
            'id': comment.id,
            'username': comment.author.username,
            'content': comment.content,
            'replies': replies
        })

    data = {
        'id': post.id,
        'author': post.author.username,
        'author_img': post.author.profile_photo.url if post.author.profile_photo else None,
        'content': post.content,
        'images': images,
        'like_count': post.like_users.count(),
        'is_liked': request.user in post.like_users.all() if request.user.is_authenticated else False,
        'comments': comments_data,
        'created_at': post.created_at.strftime('%Y-%m-%d')
    }
    return JsonResponse(data)

# 4. 댓글 등록 (대댓글 지원)
@login_required
@require_POST
def comment_add_ajax(request):
    data = json.loads(request.body)
    post_id = data.get('post_id')
    content = data.get('content')
    parent_id = data.get('parent_id')

    post = get_object_or_404(Post, pk=post_id)
    parent_comment = None
    if parent_id:
        parent_comment = get_object_or_404(Comment, pk=parent_id)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
        parent=parent_comment
    )

    return JsonResponse({
        'id': comment.id,
        'username': comment.author.username,
        'content': comment.content,
        'parent_id': parent_id
    })

# 5. 좋아요
@login_required
@require_POST
def like_ajax(request):
    data = json.loads(request.body)
    post_id = data.get('id')
    post = get_object_or_404(Post, pk=post_id)
    
    if post.like_users.filter(pk=request.user.pk).exists():
        post.like_users.remove(request.user)
        is_liked = False
    else:
        post.like_users.add(request.user)
        is_liked = True
    
    return JsonResponse({'is_liked': is_liked, 'count': post.like_users.count()})

# 6. 게시글 작성
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            images = request.FILES.getlist('photos')
            for image in images:
                PostImage.objects.create(post=post, photo=image)
            return redirect('posts:post_list')
    else:
        form = PostForm()
    return render(request, 'posts/post_create.html', {'form': form})

# 7. 게시글 삭제
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        post.delete()
    return redirect('posts:post_list')