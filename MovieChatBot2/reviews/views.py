from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
import json
from django.core.paginator import Paginator

from .models import Review, Genre
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
    
    if tmdb_id:
        details = get_movie_details(tmdb_id) # utils.py의 상세 정보 호출
        if details:
            # 1. 기본 정보 설정
            initial_data = {
                'title': details['title'],
                'director': details['director'],
                'cast': details['cast'],
                'release_year': details['release_year'],
                'runtime': details['runtime'],
                'content': details['overview'],
            }
            
            # 2. 장르 다중 선택(M2M) 처리
            genre_names = details.get('genre', '').split(', ')
            genre_objects = []
            for name in genre_names:
                # DB에 장르가 있으면 가져오고, 없으면 새로 만듭니다
                genre_obj, _ = Genre.objects.get_or_create(name=name.strip())
                genre_objects.append(genre_obj)
            
            # [핵심] ManyToMany 필드의 초기값은 ID 리스트나 객체 리스트여야 합니다.
            initial_data['genres'] = genre_objects

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save()
            return redirect('review_list')
    else:
        # initial 데이터를 가진 폼 생성 (여기서 장르가 체크됩니다!)
        form = ReviewForm(initial=initial_data)
        
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
        messages.error(request, "TMDB에서 데이터를 가져오지 못했습니다.")
        return redirect('review_list')

    count = 0
    for m in movie_list:
        details = get_movie_details(m['id'])
        
        # 기본 정보 업데이트 또는 생성
        review, created = Review.objects.update_or_create(
            tmdb_id=m['id'],
            defaults={
                'title': m['title'],
                'release_year': int(m['release_date'][:4]) if m.get('release_date') else 0,
                'director': details.get('director', '정보 없음') if details else '정보 없음',
                'cast': details.get('cast', '정보 없음') if details else '정보 없음',
                'runtime': details.get('runtime', 0) if details else 0,
                'is_tmdb': True,
                'poster_path': f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get('poster_path') else '',
                'content': m.get('overview', ''),
            }
        )

        # [핵심] 장르 다중 연결 로직
        if details and details.get('genre'):
            genre_names = details['genre'].split(', ')
            for name in genre_names:
                genre_obj, _ = Genre.objects.get_or_create(name=name.strip())
                review.genres.add(genre_obj) # 복수 장르 추가

        if created: count += 1
            
    messages.success(request, f"총 {count}개의 영화를 다중 장르 정보와 함께 가져왔습니다.")
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

def init_genres(request):
    genre_list = [
        '액션', '모험', '애니메이션', '코미디', '범죄', '다큐멘터리', '드라마', '가족', 
        '판타지', '역사', '공포', '음악', '미스터리', '로맨스', 'SF', 'TV 영화', 
        '스릴러', '전쟁', '서부', '예술', '스포츠', '느와르'
    ]
    
    count = 0
    for name in genre_list:
        genre_obj, created = Genre.objects.get_or_create(name=name)
        if created: count += 1
            
    messages.success(request, f"{count}개의 새로운 장르 카테고리가 추가되었습니다.")
    return redirect('review_list')