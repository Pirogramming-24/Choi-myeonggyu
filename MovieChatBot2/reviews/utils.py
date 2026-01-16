# reviews/utils.py

import os
import requests

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
                break # 에러 발생 시 반복 중단
        except Exception as e:
            print(f"❌ 서버 연결 중 에러 발생: {e}")
            break

    return all_movies