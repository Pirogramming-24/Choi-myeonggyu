import os
from openai import OpenAI
from .models import Review

def get_ai_response(user_message):
    client = OpenAI(
        api_key=os.getenv('UPSTAGE_API_KEY'),
        base_url="https://api.upstage.ai/v1/solar"
    )

    # 1. 내 DB에서 수집한 영화의 모든 상세 정보를 텍스트로 변환
    all_movies = Review.objects.all()
    context = "내 영화 데이터베이스 (이미 리뷰를 작성했거나 수집한 목록):\n"
    
    for movie in all_movies:
        # 감독, 출연진, 러닝타임 정보까지 포함하여 AI가 완벽하게 인지하도록 합니다.
        context += (
            f"- 제목: {movie.title} | 장르: {movie.genre} | 감독: {movie.director} | "
            f"배우: {movie.cast} | 개봉: {movie.release_year} | "
            f"러닝타임: {movie.runtime_display} | 줄거리: {movie.content[:100]}...\n"
        )

    # 2. 업스테이지 솔라 모델에게 역할과 지침 부여
    response = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {
                "role": "system", 
                "content": (
                    "너는 고도화된 영화 추천 전문가야. 다음 지침을 엄격히 따라줘:\n"
                    f"1. 아래 제공된 [내 영화 데이터베이스]를 먼저 검색해서 사용자의 질문에 답해줘.\n"
                    "2. 만약 질문한 영화가 목록에 없다면, 네가 가진 방대한 외부 영화 지식을 활용해 답변해줘.\n"
                    "3. 추천할 때는 '당신이 본 영화 중에서는 A가 좋겠고, 새로운 영화를 원하신다면 B를 추천합니다'와 같이 비교해서 설명해줘.\n\n"
                    f"{context}"
                )
            },
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content