from django.shortcuts import render, redirect, get_object_or_404 # get_object_or_404 추가!
from .models import DevTool, Idea  # DB에서 개발툴 데이터를 가져오기 위해 import
from django.http import JsonResponse # JSON 응답을 위해 필요
from django.views.decorators.http import require_POST # POST 요청만 받기 위해
from django.contrib.auth.decorators import login_required # 로그인 체크
from .models import Idea, IdeaStar
from django.db.models import Count # annotate용
from django.core.paginator import Paginator # 페이징을 위한 도구 임포트 (필수!)

# Create your views here.

def devtool_list(request):
    # 1. DB에 있는 모든 DevTool 데이터를 가져온다.
    devtools = DevTool.objects.all()
    
    # 2. 가져온 데이터를 HTML 파일(템플릿)에 'devtools'라는 이름으로 포장해서 보낸다.
    ctx = {'devtools': devtools}
    return render(request, 'ideas/devtool_list.html', ctx)

def devtool_create(request):
    # 1. 사용자가 '저장' 버튼을 눌러서 데이터를 보냈을 때 (POST 방식)
    if request.method == 'POST':
        # HTML 폼에서 보낸 데이터 꺼내기 (name 속성값으로 찾음)
        name = request.POST['name']
        kind = request.POST['kind']
        content = request.POST['content']
        
        # DB에 저장하기 (Create)
        DevTool.objects.create(name=name, kind=kind, content=content)
        
        # 저장이 끝나면 리스트 페이지로 이동 (Redirect)
        return redirect('ideas:devtool_list')

    # 2. 사용자가 그냥 링크를 타고 들어왔을 때 (GET 방식) -> 빈 폼 보여주기
    return render(request, 'ideas/devtool_create.html')

def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    
    # [추가] URL 꼬리표에서 '어디서 왔는지(prev)'와 '아이디어 번호(idea_pk)'를 꺼냅니다.
    # 만약 그냥 들어왔으면 None이 됩니다.
    prev = request.GET.get('prev')
    idea_pk = request.GET.get('idea_pk')
    
    ctx = {
        'devtool': devtool,
        'prev': prev,       # 템플릿으로 전달
        'idea_pk': idea_pk, # 템플릿으로 전달
    }
    return render(request, 'ideas/devtool_detail.html', ctx)

# 1. 삭제 기능
def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    
    if request.method == 'POST':
        devtool.delete() # DB에서 삭제
        return redirect('ideas:devtool_list') # 삭제 후 목록으로 이동
    
    # (선택) 실수로 삭제하는 걸 방지하기 위해 POST가 아니면 삭제 안 함
    return redirect('ideas:devtool_detail', pk=pk)

# 2. 수정 기능
def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)

    if request.method == 'POST':
        # 수정된 데이터 받아서 덮어쓰기
        devtool.name = request.POST['name']
        devtool.kind = request.POST['kind']
        devtool.content = request.POST['content']
        devtool.save() # DB에 반영 (저장)
        
        return redirect('ideas:devtool_detail', pk=devtool.pk) # 상세 페이지로 이동

    # GET 요청: 기존 데이터가 담긴 페이지 보여주기
    # 템플릿에서 기존 값을 보여주려면 'devtool'을 넘겨줘야 함!
    ctx = {'devtool': devtool}
    return render(request, 'ideas/devtool_update.html', ctx)

def idea_list(request):
    # 1. 정렬 기준 가져오기
    sort = request.GET.get('sort', 'recent')

    # 2. 정렬 로직 (이 부분은 잘 하셨습니다)
    if sort == 'recent':
        ideas = Idea.objects.all().order_by('-created_at')
    elif sort == 'oldest':
        ideas = Idea.objects.all().order_by('created_at')
    elif sort == 'likes':
        ideas = Idea.objects.annotate(star_count=Count('stars')).order_by('-star_count', '-created_at')
    elif sort == 'interest':
        ideas = Idea.objects.all().order_by('-interest', '-created_at')
    elif sort == 'name':
        ideas = Idea.objects.all().order_by('title')
    else:
        ideas = Idea.objects.all().order_by('-created_at')

    # 3. 페이지네이션
    paginator = Paginator(ideas, 4) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ---------------------------------------------------------
    # [중요!] 여기가 핵심입니다. 
    # 이 코드가 if/elif 문 안에 들어가 있으면 안 됩니다!
    # 무조건 실행되도록 바깥으로 빼주세요.
    # ---------------------------------------------------------
    starred_idea_ids = []
    if request.user.is_authenticated:
        # 내가 찜한 아이디어 ID들을 리스트로 뽑아옴 (예: [1, 5, 8])
        starred_idea_ids = list(IdeaStar.objects.filter(user=request.user).values_list('idea_id', flat=True))
    # ---------------------------------------------------------

    # 4. 템플릿 전달
    ctx = {
        'ideas': page_obj,
        'sort': sort,
        'starred_idea_ids': starred_idea_ids # 이걸 꼭 보내줘야 HTML이 별을 칠할 수 있습니다
    }
    return render(request, 'ideas/idea_list.html', ctx)

def idea_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        
        # [수정] 문자열을 숫자로 바꾼 뒤, 범위를 0~7로 강제 고정
        interest = int(request.POST['interest'])
        if interest > 7:
            interest = 7
        elif interest < 0:
            interest = 0
            
        devtool_id = request.POST['devtool']
        devtool = DevTool.objects.get(pk=devtool_id)
        image = request.FILES.get('image')

        Idea.objects.create(
            title=title,
            content=content,
            interest=interest, # 고정된 값 저장
            devtool=devtool,
            image=image
        )
        return redirect('ideas:idea_list')

    # GET 요청: 등록 폼 보여주기
    # ★중요: 개발툴을 '선택'해야 하니까, 모든 개발툴 목록을 가져가야 함
    devtools = DevTool.objects.all()
    ctx = {'devtools': devtools}
    return render(request, 'ideas/idea_create.html', ctx)

# ideas/views.py

def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    
    # [추가] 접속한 사람이 이 글을 찜했는지 확인 (True/False)
    is_starred = False
    if request.user.is_authenticated:
        is_starred = IdeaStar.objects.filter(user=request.user, idea=idea).exists()

    ctx = {
        'idea': idea,
        'is_starred': is_starred # 템플릿으로 전달
    }
    return render(request, 'ideas/idea_detail.html', ctx)

# 4. 아이디어 수정 (Update)
def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        idea.title = request.POST['title']
        idea.content = request.POST['content']
        
        # [수정] 여기도 똑같이 제한 로직 추가
        new_interest = int(request.POST['interest'])
        if new_interest > 7:
            new_interest = 7
        elif new_interest < 0:
            new_interest = 0
        idea.interest = new_interest
        
        devtool_id = request.POST['devtool']
        idea.devtool = DevTool.objects.get(pk=devtool_id)

        if request.FILES.get('image'):
            idea.image = request.FILES.get('image')
            
        idea.save()
        return redirect('ideas:idea_detail', pk=idea.pk)

    # GET 요청: 수정 폼 보여주기 (기존 값 채워서)
    devtools = DevTool.objects.all()
    ctx = {
        'idea': idea,
        'devtools': devtools
    }
    return render(request, 'ideas/idea_update.html', ctx)

# 5. 아이디어 삭제 (Delete)
def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    
    if request.method == 'POST':
        idea.delete()
        return redirect('ideas:idea_list')
    
    return redirect('ideas:idea_detail', pk=pk)

# 6. 관심도 조정 (AJAX)
@require_POST
def idea_interest(request, pk, action):
    idea = get_object_or_404(Idea, pk=pk)
    
    if action == 'up':
        # [수정] 7점 미만일 때만 1 증가 (최대 7점)
        if idea.interest < 7:
            idea.interest += 1
            
    elif action == 'down':
        # [수정] 0점 초과일 때만 1 감소 (최소 0점 - 음수 방지)
        if idea.interest > 0:
            idea.interest -= 1
            
    idea.save()
    
    # 변경된 값을 JSON으로 돌려줌
    return JsonResponse({'interest': idea.interest})

# 7. 찜하기 토글 (AJAX)
@login_required # 로그인한 사람만 가능!
@require_POST
def idea_star(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    user = request.user

    # 이미 찜했는지 확인
    star, created = IdeaStar.objects.get_or_create(user=user, idea=idea)

    if not created:
        # 이미 존재하면 -> 삭제 (찜 취소)
        star.delete()
        is_starred = False
    else:
        # 새로 만들었으면 -> 유지 (찜하기)
        is_starred = True
    
    # 현재 찜 상태를 JSON으로 돌려줌
    return JsonResponse({'is_starred': is_starred})