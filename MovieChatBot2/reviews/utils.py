import os
import requests

# [추가] TMDB 장르 ID를 한글 이름으로 변환하기 위한 맵
TMDB_GENRE_MAP = {
    28: '액션', 12: '모험', 16: '애니메이션', 35: '코미디', 80: '범죄',
    99: '다큐멘터리', 18: '드라마', 10751: '가족', 14: '판타지', 36: '역사',
    27: '공포', 10402: '음악', 9648: '미스터리', 10749: '로맨스', 878: 'SF',
    10770: 'TV 영화', 53: '스릴러', 10752: '전쟁', 37: '서부'
}

# 1. 인기 영화 목록 가져오기 (메인/리뷰 리스트용)
def fetch_tmdb_popular_movies():
    ACCESS_TOKEN = os.getenv('TMDB_ACCESS_TOKEN') 
    
    if not ACCESS_TOKEN:
        print("❌ DEBUG: .env에서 TMDB_ACCESS_TOKEN을 찾을 수 없습니다.")
        return []

    all_movies = []
    # 1페이지부터 2페이지까지 반복 (페이지당 20개 x 2 = 40개)
    for page in range(1, 3):
        url = f"https://api.themoviedb.org/3/movie/popular?language=ko-KR&page={page}"
        
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                results = response.json().get('results', [])
                all_movies.extend(results) # 가져온 리스트를 전체 리스트에 합침
                print(f"✅ DEBUG: {page}페이지 로드 성공 ({len(results)}개)")
            else:
                print(f"❌ TMDB API 에러 ({page}페이지): {response.status_code}")
                break 
        except Exception as e:
            print(f"❌ 서버 연결 중 에러 발생: {e}")
            break

    return all_movies

# 2. 영화 검색하기 (검색창 결과용)
def search_tmdb_movies(query):
    token = os.getenv('TMDB_ACCESS_TOKEN')
    url = f"https://api.themoviedb.org/3/search/movie?query={query}&language=ko-KR&page=1"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json().get('results', [])
        # [수정] 각 영화 데이터의 숫자 장르 ID를 한글 이름으로 변환하여 추가
        for movie in results:
            genre_ids = movie.get('genre_ids', [])
            movie['genre_names'] = ", ".join([TMDB_GENRE_MAP.get(gid, "기타") for gid in genre_ids])
        return results
    return []

# 3. 영화 상세 정보 가져오기 (감독, 배우, 런타임 등)
def get_movie_details(movie_id):
    token = os.getenv('TMDB_ACCESS_TOKEN')
    # credits(배우/제작진) 정보를 포함해서 가져옵니다.
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=ko-KR&append_to_response=credits"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        # 감독 추출
        director = next((m['name'] for m in data['credits']['crew'] if m['job'] == 'Director'), "알 수 없음")
        
        # 주연 배우 상위 3명 추출
        cast = ", ".join([m['name'] for m in data['credits']['cast'][:3]])
        
        # 장르 이름을 콤마로 연결 (나중에 DB 저장 시 활용)
        genres = ", ".join([g['name'] for g in data.get('genres', [])])
        
        return {
            'title': data.get('title'),
            'director': director,
            'cast': cast,
            'genre': genres,
            'release_year': data.get('release_date', '')[:4],
            'runtime': data.get('runtime'),
            'poster_path': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else '',
            'overview': data.get('overview'),
        }
    return None