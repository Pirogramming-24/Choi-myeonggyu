from django.shortcuts import render, redirect, get_object_or_404
from .models import Review
from .forms import ReviewForm

# Create your views here.
def main(request):
    return render(request, "main.html")

# 기능 1: 리뷰 리스트
def review_list(request):
    # 1. 사용자가 주소창에 보낸 장르(genre) 가져오기 (없으면 None)
    genre_query = request.GET.get('genre')
    
    # 2. 일단 모든 리뷰를 최신순으로 가져옵니다.
    reviews = Review.objects.all().order_by('-created_at')

    # 3. 만약 특정 장르를 선택했다면? -> 그 장르만 남기고 필터링
    if genre_query:
        reviews = reviews.filter(genre=genre_query)

    # 4. 화면에 뿌려줄 장르 목록 (forms.py에 썼던 것과 똑같아야 합니다!)
    genres = [
        '액션 영화', '모험 영화', '예술 영화', '코미디 영화', '다큐멘터리 영화', '드라마 영화',
        '교육 영화', '서사 영화', '실험 영화', '엑스플로이테이션 영화', '판타지 영화', '누아르 영화',
        '공포 영화', '멈블코어', '뮤지컬 영화', '미스터리 영화', '로맨스 영화', '일상물',
        '애니메이션', '드라마'
    ]

    context = {
        'reviews': reviews,
        'genres': genres,
        'selected_genre': genre_query, # 현재 선택된 장르가 뭔지 화면에 알려줌
    }
    
    return render(request, 'review_list.html', context)

# 기능 4: 리뷰 디테일
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'review_detail.html', {'review': review})

# reviews/views.py

# 기능 8 & 10: 리뷰 작성
def review_create(request):
    if request.method == "POST":
        # 수정 전: form = ReviewForm(request.POST) 
        # 수정 후: request.FILES를 반드시 추가해야 합니다!
        form = ReviewForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form': form, 'action': '작성'})

# 기능 9 & 11: 리뷰 수정
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        # 여기도 마찬가지로 request.FILES 추가!
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review_detail', pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'review_form.html', {'form': form, 'action': '수정'})

# 기능 7: 리뷰 삭제
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
        return redirect('review_list')
    return redirect('review_detail', pk=pk) # POST 요청이 아니면 다시 디테일로