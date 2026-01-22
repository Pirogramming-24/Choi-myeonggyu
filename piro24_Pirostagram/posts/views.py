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
from django.db.models import Count
from django.db.models import Q

# 1. 메인 피드
# posts/views.py

def post_list(request):
    sort = request.GET.get('sort', 'latest') # URL 쿼리스트링에서 정렬 기준 가져오기 (기본값: latest)
    q = request.GET.get('q', '') # 검색어 가져오기
    
    # 1. 기본 쿼리셋 생성 (최적화 포함)
    # annotate를 미리 해둬야 정렬 시 오류가 없습니다.
    posts = Post.objects.annotate(like_count=Count('like_users')).prefetch_related(
        'images', 
        'comments', 
        'comments__author', 
        'comments__replies', 
        'comments__replies__author'
    )
    # ✅ [검색 기능] 내용에 검색어가 포함된 글 필터링
    if q:
        posts = posts.filter(content__icontains=q)
    # 2. 정렬 조건 적용
    if sort == 'likes':
        # 좋아요 순 (동점일 경우 최신순)
        posts = posts.order_by('-like_count', '-created_at')
    else:
        # 최신순 (기본)
        posts = posts.order_by('-created_at')
    
    # ---------------------------------------------------------
    # ❌ 삭제 대상: 아래 코드가 위에서 정렬한 posts를 덮어쓰고 있었습니다!
    # posts = Post.objects.all().order_by('-created_at')... (이 부분 삭제)
    # ---------------------------------------------------------

    # --- (아래 스토리 로직은 기존 그대로 유지) ---
    
    # 24시간 내 스토리 가져오기
    one_day_ago = timezone.now() - timedelta(hours=24)
    active_stories = Story.objects.filter(created_at__gte=one_day_ago).select_related('author').order_by('created_at')
    
    user_has_story = False
    if request.user.is_authenticated:
        user_has_story = active_stories.filter(author=request.user).exists()

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
        'user_has_story': user_has_story,
        'sort': sort, # ✅ 템플릿에서 현재 정렬 상태를 알기 위해 전달 (파란색 표시용)
        'q': q, # 검색어 템플릿으로 전달
    }
    return render(request, 'posts/post_list.html', ctx)

# 2. 게시글 수정 (New)
@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        return redirect('posts:post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            
            # ✅ 1. 기존 사진 삭제 로직
            # HTML에서 name='delete_images'로 체크된 이미지 ID 리스트를 받음
            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                # 해당 ID의 이미지들을 DB와 파일시스템에서 삭제
                for img_id in delete_ids:
                    image = PostImage.objects.filter(pk=img_id, post=post).first()
                    if image:
                        image.delete() # 모델 delete 호출 시 파일도 삭제됨 (설정에 따라 다름)

            # ✅ 2. 새 사진 추가 로직
            new_images = request.FILES.getlist('photos')
            for image in new_images:
                PostImage.objects.create(post=post, photo=image)

            return redirect('posts:post_list')
    else:
        form = PostForm(instance=post)
        
    return render(request, 'posts/post_update.html', {'form': form, 'post': post})

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

# 3. 댓글 삭제 (Ajax) (New)
@login_required
@require_POST
def comment_delete_ajax(request):
    data = json.loads(request.body)
    comment = get_object_or_404(Comment, pk=data.get('comment_id'))
    
    if comment.author == request.user:
        comment.delete()
        return JsonResponse({'deleted': True})
    return JsonResponse({'deleted': False}, status=403)

# 4. 댓글 수정 (Ajax) (New)
@login_required
@require_POST
def comment_update_ajax(request):
    data = json.loads(request.body)
    comment = get_object_or_404(Comment, pk=data.get('comment_id'))
    
    if comment.author == request.user:
        comment.content = data.get('content')
        comment.save()
        return JsonResponse({'updated': True, 'content': comment.content})
    return JsonResponse({'updated': False}, status=403)

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