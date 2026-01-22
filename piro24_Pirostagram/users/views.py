from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model # get_user_model 추가
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required # ✅ 이 줄이 빠져서 에러가 났던 겁니다!
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from .models import User, Notification # Notification 추가
import json

# ✅ User 모델을 변수에 담아줘야 아래 코드에서 User.objects... 를 쓸 수 있습니다.
User = get_user_model()

# 1. 로그인
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('posts:post_list') # 로그인 성공 시 메인 피드로 이동
    else:
        form = AuthenticationForm()
    
    ctx = {'form': form}
    return render(request, 'users/login.html', ctx)

# 2. 로그아웃
def logout_view(request):
    logout(request)
    return redirect('users:login') # 로그아웃 후 로그인 화면으로 이동

# 3. 회원가입
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES) # 프로필 사진 처리를 위해 FILES 추가
        if form.is_valid():
            user = form.save()
            login(request, user) # 회원가입 후 자동 로그인
            return redirect('posts:post_list')
    else:
        form = CustomUserCreationForm()
        
    ctx = {'form': form}
    return render(request, 'users/signup.html', ctx)

# 1. 유저 검색 뷰
def search_view(request):
    query = request.GET.get('q', '') # 검색어 가져오기
    if query:
        users = User.objects.filter(username__icontains=query) # 이름에 검색어가 포함된 유저 찾기
    else:
        users = []
    
    return render(request, 'users/search_result.html', {'users': users, 'query': query})

# 2. 유저 프로필 뷰
def profile_view(request, username):
    user_info = get_object_or_404(User, username=username)
    # 해당 유저가 작성한 게시글 가져오기
    posts = user_info.posts.all().order_by('-created_at')
    
    ctx = {
        'user_info': user_info,
        'posts': posts,
    }
    return render(request, 'users/profile.html', ctx)

# 3. 팔로우 토글 (Ajax)
@login_required
@require_POST
def follow_ajax(request, user_id):
    # 1. 팔로우 할 대상 찾기
    target_user = get_object_or_404(User, pk=user_id)
    me = request.user
    
    # 자기 자신 팔로우 방지
    if me == target_user:
        return JsonResponse({'error': '스스로를 팔로우할 수 없습니다.'}, status=400)

    if me.followings.filter(pk=target_user.pk).exists():
        me.followings.remove(target_user)
        is_followed = False
    else:
        me.followings.add(target_user)
        is_followed = True
        
        # ✅ 알림 생성 코드 추가!
        Notification.objects.create(
            recipient=target_user,
            sender=me,
            message=f"{me.username}님이 회원님을 팔로우하기 시작했습니다."
        )
    
    # 3. 결과 응답 (팔로워 숫자 갱신용)
    return JsonResponse({
        'is_followed': is_followed,
        'followers_count': target_user.followers.count(),
        'followings_count': target_user.followings.count(),
    })

def follow_list_view(request, user_id, kind):
    page_user = get_object_or_404(User, pk=user_id)
    
    if kind == 'followers':
        users = page_user.followers.all()
        title = f"{page_user.username}님의 팔로워"
    else: # followings
        users = page_user.followings.all()
        title = f"{page_user.username}님의 팔로잉"

    ctx = {
        'users': users,
        'title': title,
    }
    return render(request, 'users/follow_list.html', ctx)

@login_required
def notification_view(request):
    # 내 알림을 최신순으로 가져옴
    notis = request.user.notifications.all().order_by('-created_at')
    return render(request, 'users/notifications.html', {'notis': notis})