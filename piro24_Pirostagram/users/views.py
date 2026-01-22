from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from posts.models import Notification # 알림 모델
import json

User = get_user_model()

# 1. 로그인
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('posts:post_list')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# 2. 로그아웃
def logout_view(request):
    logout(request)
    return redirect('users:login')

# 3. 회원가입
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('posts:post_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

# 4. 유저 프로필
@login_required
def profile_view(request, username):
    user_info = get_object_or_404(User, username=username)
    posts = user_info.posts.all().order_by('-created_at') # 게시글 가져오기
    
    ctx = {
        'user_info': user_info,
        'posts': posts,
        'followers_count': user_info.followers.count(), # 템플릿 편의용
        'followings_count': user_info.followings.count(),
        'is_followed': user_info.followers.filter(pk=request.user.pk).exists() if request.user != user_info else False
    }
    return render(request, 'users/profile.html', ctx)

# 5. 팔로우 토글 (Ajax) - 버그 수정됨
@login_required
@require_POST
def follow_ajax(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    me = request.user
    
    if me == target_user:
        return JsonResponse({'error': '스스로를 팔로우할 수 없습니다.'}, status=400)

    # 이미 팔로우 중이면 -> 취소
    if me.followings.filter(pk=target_user.pk).exists():
        me.followings.remove(target_user)
        is_followed = False
    else:
        # 팔로우 안했으면 -> 추가
        me.followings.add(target_user)
        is_followed = True
        
        # ✅ [핵심 수정] recipient -> receiver 로 변경
        # 중복 알림 방지 체크 후 생성
        if not Notification.objects.filter(receiver=target_user, sender=me, type='follow', is_read=False).exists():
            Notification.objects.create(
                receiver=target_user, # 여기가 틀렸었습니다!
                sender=me,
                type='follow',
                message=f"{me.username}님이 회원님을 팔로우하기 시작했습니다.",
                url=f"/users/{me.username}/" # 내 프로필로 이동
            )
    
    return JsonResponse({
        'is_followed': is_followed,
        'followers_count': target_user.followers.count(),
        'followings_count': target_user.followings.count(),
    })

# 6. 유저 검색 (별도 페이지용, 혹시 필요하면 유지)
def search_view(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query) if query else []
    return render(request, 'users/search_result.html', {'users': users, 'query': query})

# 7. 팔로우 리스트
def follow_list_view(request, user_id, kind):
    page_user = get_object_or_404(User, pk=user_id)
    if kind == 'followers':
        users = page_user.followers.all()
        title = f"{page_user.username}님의 팔로워"
    else:
        users = page_user.followings.all()
        title = f"{page_user.username}님의 팔로잉"
    return render(request, 'users/follow_list.html', {'users': users, 'title': title})

# 8. 알림 페이지 (Ajax가 안될 때 대비용)
@login_required
def notification_view(request):
    notis = request.user.notifications.all().order_by('-created_at')
    return render(request, 'users/notifications.html', {'notis': notis})