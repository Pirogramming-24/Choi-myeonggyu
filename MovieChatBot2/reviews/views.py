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
from .utils import search_tmdb_movies, get_movie_details # utils.py에 정의한 함수들

# 1. 메인 페이지
def main(request):
    return render(request, "main.html")

# 2. 리뷰 리스트 (통계 대시보드 및 필터 포함)
def review_list(request):
    # 1. 파라미터 가져오기
    genre_query = request.GET.get('genre')
    search_query = request.GET.get('q')
    source_query = request.GET.get('source', 'all')
    sort_query = request.GET.get('sort', '-created_at') # 기본값: 최신 추가순

    # 2. 통계 데이터 계산 (필터링 전 전체 기준)
    total_count = Review.objects.count()
    tmdb_count = Review.objects.filter(is_tmdb=True).count()
    user_count = Review.objects.filter(is_tmdb=False).count()

    # 3. 기본 쿼리셋 설정
    reviews = Review.objects.all()

    # 4. 출처 필터링 (노란색 동그라미)
    if source_query == 'tmdb':
        reviews = reviews.filter(is_tmdb=True)
    elif source_query == 'user':
        reviews = reviews.filter(is_tmdb=False)

    # 5. 장르 필터링 (복구)
    if genre_query:
        reviews = reviews.filter(genre=genre_query)

    # 6. 검색 로직
    if search_query:
        reviews = reviews.filter(
            Q(title__icontains=search_query) | 
            Q(director__icontains=search_query) | 
            Q(cast__icontains=search_query)
        )

    # 7. 정렬 로직 (초록색 동그라미 - 최신 영화순 추가)
    # -created_at: 최신 추가순 / -rating: 별점순 / -release_year: 최신 영화순
    reviews = reviews.order_by(sort_query)

    # 8. 페이지네이션 (8개씩)
    paginator = Paginator(reviews, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = [
        '액션 영화', '모험 영화', '예술 영화', '코미디 영화', '다큐멘터리 영화', '드라마 영화',
        '교육 영화', '서사 영화', '실험 영화', '판타지 영화', '누아르 영화',
        '공포 영화', '뮤지컬 영화', '미스터리 영화', '로맨스 영화', '애니메이션', '드라마'
    ]

    context = {
        'reviews': page_obj,
        'genres': genres,
        'total_count': total_count,
        'tmdb_count': tmdb_count,
        'user_count': user_count,
        'selected_genre': genre_query,
        'search_query': search_query,
        'selected_source': source_query,
        'selected_sort': sort_query,
    }
    return render(request, 'review_list.html', context)

# 3. 리뷰 상세 보기
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'review_detail.html', {'review': review})

# [추가] 1. 영화 검색 페이지 뷰
def movie_search(request):
    query = request.GET.get('q')
    movies = []
    if query:
        movies = search_tmdb_movies(query) # utils.py에서 검색 결과 가져옴
    return render(request, 'movie_search.html', {'movies': movies, 'query': query})

# [추가] 2. 에러 해결을 위한 AJAX 함수 (상세 정보 반환)
def get_tmdb_details_ajax(request, tmdb_id):
    details = get_movie_details(tmdb_id)
    if details:
        return JsonResponse(details)
    return JsonResponse({'error': '데이터를 가져오지 못했습니다.'}, status=404)

# [수정] 3. 리뷰 작성 뷰 (자동 완성 로직 포함)
def review_create(request):
    initial_data = {}
    tmdb_id = request.GET.get('tmdb_id')
    
    # 검색 결과에서 '리뷰 쓰기'를 눌러 들어온 경우
    if tmdb_id:
        details = get_movie_details(tmdb_id)
        if details:
            initial_data = {
                'title': details['title'],
                'director': details['director'],
                'cast': details['cast'],
                'genre': details['genre'],
                'release_year': details['release_year'],
                'runtime': details['runtime'],
                'content': details['overview'],
            }

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            # TMDB 연동 데이터가 있다면 수동으로 필드 채우기
            if request.POST.get('tmdb_id'):
                review.tmdb_id = request.POST.get('tmdb_id')
                review.is_tmdb = True
                review.poster_path = request.POST.get('poster_path')
            review.save()
            return redirect('review_list')
    else:
        # initial 인자를 통해 폼에 미리 데이터를 채워줍니다.
        form = ReviewForm(initial=initial_data)
        
    return render(request, 'review_form.html', {
        'form': form, 
        'action': '작성', 
        'tmdb_id': tmdb_id,
        'poster_path': details['poster_path'] if tmdb_id and details else ''
    })

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
        # [핵심 추가] 각 영화의 ID로 상세 정보(감독, 배우, 러닝타임 등)를 가져옵니다.
        details = get_movie_details(m['id'])
        
        # 상세 정보를 가져오는 데 성공했다면 해당 데이터를 사용하고, 실패하면 기본값을 사용합니다.
        if details:
            director = details.get('director', '정보 없음')
            cast = details.get('cast', '정보 없음')
            runtime = details.get('runtime', 0)
            genre = details.get('genre', '드라마')
        else:
            director = '정보 없음'
            cast = '정보 없음'
            runtime = 0
            genre = '드라마'

        obj, created = Review.objects.update_or_create(
            tmdb_id=m['id'],
            defaults={
                'title': m['title'],
                'release_year': int(m['release_date'][:4]) if m.get('release_date') else 0,
                'director': director,  # 상세 정보 적용
                'cast': cast,          # 상세 정보 적용
                'runtime': runtime,    # 상세 정보 적용
                'genre': genre,        # 상세 정보 적용
                'is_tmdb': True,
                'poster_path': f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get('poster_path') else '',
                'content': m.get('overview', ''),
                'rating': 0,
            }
        )
        if created: count += 1
            
    if count > 0:
        messages.success(request, f"상세 정보까지 포함된 새로운 영화 {count}개를 가져왔습니다!")
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
    
def delete_all_tmdb(request):
    # is_tmdb가 True인 데이터만 골라서 삭제합니다.
    deleted_count, _ = Review.objects.filter(is_tmdb=True).delete()
    messages.success(request, f"성공적으로 {deleted_count}개의 TMDB 데이터를 삭제했습니다.")
    return redirect('review_list')