import os
from openai import OpenAI  # 업스테이지 권장 라이브러리 (연결 도구일 뿐입니다)
from .models import Review

def get_ai_response(user_message):
    # 1. 업스테이지 솔라 클라이언트 설정
    client = OpenAI(
        api_key=os.getenv('UPSTAGE_API_KEY'),
        base_url="https://api.upstage.ai/v1/solar" # 호출 주소가 업스테이지입니다!
    )

    # 2. 내 DB에서 영화 정보 가져오기 (RAG 데이터 준비)
    all_movies = Review.objects.all()
    context = "내 영화 데이터베이스:\n"
    for movie in all_movies:
        # AI가 이해하기 쉽게 정보를 문자열로 합칩니다.
        context += f"- 제목: {movie.title}, 장르: {movie.genre}, 개봉: {movie.release_year}, 줄거리: {movie.content[:60]}\n"

    # 3. 솔라 모델(solar-1-mini-chat)에게 질문 던지기
    response = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {
                "role": "system", 
                "content": f"너는 영화 전문가야. 다음 제공된 목록을 참고해서 사용자의 질문에 답해줘. 목록에 있는 영화면 적극 추천하고, 없어도 비슷한 영화를 알려줘.\n\n{context}"
            },
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content