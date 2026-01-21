from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import AIHistory
from .ai_loader import analyze_sentiment, summarize_text, translate_text

# 접근 권한 체크 함수
def check_access(request):
    if not request.user.is_authenticated:
        messages.error(request, "로그인 후 이용해주세요.")
        return False
    return True

# 1. 감정분석 (공개)
def sentiment_view(request):
    result = None
    histories = []

    # POST 요청 처리 (분석 실행)
    if request.method == 'POST':
        text = request.POST.get('user_input')
        if text:
            result = analyze_sentiment(text)
            # 로그인 유저만 기록 저장
            if request.user.is_authenticated:
                AIHistory.objects.create(
                    user=request.user, 
                    model_type='sentiment', 
                    input_text=text, 
                    result_text=result
                )

    # 화면에 보여줄 기록 조회 (로그인한 경우에만 DB에서 가져옴)
    if request.user.is_authenticated:
        histories = AIHistory.objects.filter(user=request.user, model_type='sentiment').order_by('-created_at')[:5] # 최근 5개만
    else:
        histories = [] # 비로그인은 기록 없음 (새로고침 시 초기화됨)

    return render(request, 'ai_app/sentiment.html', {'result': result, 'histories': histories, 'tab': 'sentiment'})

# 2. 요약 (회원전용)
def summary_view(request):
    if not check_access(request):
        return redirect(f'/accounts/login/?next={request.path}')

    result = None
    
    if request.method == 'POST':
        text = request.POST.get('user_input')
        if text:
            result = summarize_text(text)
            AIHistory.objects.create(
                user=request.user, model_type='summary', 
                input_text=text, result_text=result
            )

    # 기록 조회
    histories = AIHistory.objects.filter(user=request.user, model_type='summary').order_by('-created_at')[:5]

    return render(request, 'ai_app/summary.html', {'result': result, 'histories': histories, 'tab': 'summary'})

# 3. 번역 (회원전용)
def translation_view(request):
    if not check_access(request):
        return redirect(f'/accounts/login/?next={request.path}')

    result = None

    if request.method == 'POST':
        text = request.POST.get('user_input')
        if text:
            result = translate_text(text)
            AIHistory.objects.create(
                user=request.user, model_type='translation', 
                input_text=text, result_text=result
            )

    histories = AIHistory.objects.filter(user=request.user, model_type='translation').order_by('-created_at')[:5]

    return render(request, 'ai_app/translation.html', {'result': result, 'histories': histories, 'tab': 'translation'})

# 4. 콤보 (회원전용)
def combo_view(request):
    if not check_access(request):
        return redirect(f'/accounts/login/?next={request.path}')
    
    final_result = None

    if request.method == 'POST':
        original_text = request.POST.get('user_input')
        if original_text:
            summary_result = summarize_text(original_text)
            translation_result = translate_text(summary_result)

            final_result = {
                'original': original_text,
                'summary': summary_result,
                'translation': translation_result
            }

            AIHistory.objects.create(
                user=request.user, model_type='combo', 
                input_text=original_text[:30] + "...", 
                result_text=f"[요약+번역] {translation_result}"
            )

    histories = AIHistory.objects.filter(user=request.user, model_type='combo').order_by('-created_at')[:5]

    return render(request, 'ai_app/combo.html', {'result': final_result, 'histories': histories, 'tab': 'combo'})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 가입 후 바로 자동 로그인
            return redirect('/')  # 메인 페이지로 이동
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})