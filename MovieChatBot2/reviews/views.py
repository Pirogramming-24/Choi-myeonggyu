from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
import json
from django.core.paginator import Paginator

from .models import Review
from .forms import ReviewForm
from .utils import fetch_tmdb_popular_movies
from .ai_utils import get_ai_response  # AI 로직 연동

# 1. 메인 페이지
def main(request):
    return render(request, "main.html")

# 2. 리뷰 리스트 (통계 대시보드 및 필터 포함)
def review_list(request):
    genre_query = request.GET.get('genre')
    search_query = request.GET.get('q')
    sort_query = request.GET.get('sort', '-created_at')
    source_query = request.GET.get('source', 'all')

    # 통계 계산
    total_count = Review.objects.count()
    tmdb_count = Review.objects.filter(is_tmdb=True).count()
    user_count = Review.objects.filter(is_tmdb=False).count()

    reviews = Review.objects.all()

    # 필터링: 출처별
    if source_query == 'tmdb':
        reviews = reviews.filter(is_tmdb=True)
    elif source_query == 'user':
        reviews = reviews.filter(is_tmdb=False)

    # 필터링: 검색어
    if search_query:
        reviews = reviews.filter(
            Q(title__icontains=search_query) | 
            Q(director__icontains=search_query) | 
            Q(cast__icontains=search_query)
        )

    # 필터링: 장르
    if genre_query:
        reviews = reviews.filter(genre=genre_query)

    # 정렬
    reviews = reviews.order_by(sort_query)

    # [수정] 정렬까지 완료된 reviews를 가져온 후 페이지네이션 적용
    paginator = Paginator(reviews, 8) # 한 페이지에 8개씩
    page_number = request.GET.get('page') # 주소창의 ?page=2 등을 읽음
    page_obj = paginator.get_page(page_number)

    # 장르 목록 정의 (NameError 방지)
    genres = [
        '액션 영화', '모험 영화', '예술 영화', '코미디 영화', '다큐멘터리 영화', '드라마 영화',
        '교육 영화', '서사 영화', '실험 영화', '판타지 영화', '누아르 영화',
        '공포 영화', '뮤지컬 영화', '미스터리 영화', '로맨스 영화', '애니메이션', '드라마'
    ]

    context = {
        'reviews': page_obj, # 이제 reviews 대신 page_obj를 보냅니다.
        'page_obj': page_obj, # 템플릿에서 페이지 번호를 그리기 위함
        # ... (나머지 context 데이터 동일) ...
        'genres': genres,
        'total_count': total_count,
        'tmdb_count': tmdb_count,
        'user_count': user_count,
        'selected_genre': genre_query,
        'search_query': search_query,
        'selected_sort': sort_query,
        'selected_source': source_query,
    }
    return render(request, 'review_list.html', context)

# 3. 리뷰 상세 보기
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'review_detail.html', {'review': review})

# 4. 리뷰 작성
def review_create(request):
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form': form, 'action': '작성'})

# 5. 리뷰 수정
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review_detail', pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'review_form.html', {'form': form, 'action': '수정'})

# 6. 리뷰 삭제
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
        return redirect('review_list')
    return redirect('review_detail', pk=pk)

# 7. TMDB 데이터 동기화
def sync_tmdb_movies(request):
    movie_list = fetch_tmdb_popular_movies()
    if not movie_list:
        messages.error(request, "TMDB에서 데이터를 가져오지 못했습니다. API 키를 확인하세요.")
        return redirect('review_list')

    count = 0
    for m in movie_list:
        obj, created = Review.objects.update_or_create(
            tmdb_id=m['id'],
            defaults={
                'title': m['title'],
                'release_year': int(m['release_date'][:4]) if m.get('release_date') else 0,
                'genre': '드라마', 
                'is_tmdb': True,
                'poster_path': f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get('poster_path') else '',
                'content': m.get('overview', ''),
                'rating': 0,
            }
        )
        if created: count += 1
            
    if count > 0:
        messages.success(request, f"새로운 영화 {count}개를 성공적으로 가져왔습니다!")
    else:
        messages.info(request, "새로 추가할 영화가 없습니다. (이미 최신 상태)")
    return redirect('review_list')

# 8. AI 챗봇 페이지
def chatbot_page(request):
    return render(request, 'chatbot.html')

# 9. AI 챗봇 API (비동기 통신용)
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get('message')
        ai_answer = get_ai_response(user_message)
        return JsonResponse({'answer': ai_answer})