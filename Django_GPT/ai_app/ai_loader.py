import os
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

# 전역 변수 초기화
sentiment_pipeline = None
summary_pipeline = None
translator_pipeline = None

# ---------------------------------------------------------
# 모델 로드 함수 (Lazy Loading)
# ---------------------------------------------------------

def get_sentiment_model():
    global sentiment_pipeline
    if sentiment_pipeline is None:
        print("⏳ 감정분석 모델 로딩 중...")
        sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
    return sentiment_pipeline

def get_summary_model():
    global summary_pipeline
    if summary_pipeline is None:
        print("⏳ 요약 모델 로딩 중...")
        summary_pipeline = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    return summary_pipeline

def get_translator_model():
    global translator_pipeline
    if translator_pipeline is None:
        print("⏳ 번역 모델(M2M100) 로딩 중... (약 1.5GB 다운로드)")
        # ✅ Facebook M2M100 418M (경량화 모델, NLLB 아님, Helsinki 아님)
        # 영어(en) -> 한국어(ko) 설정
        translator_pipeline = pipeline("translation", model="facebook/m2m100_418M", src_lang="en", tgt_lang="ko")
    return translator_pipeline

# ---------------------------------------------------------
# 실행 함수들 (Views에서 호출하는 함수들)
# ---------------------------------------------------------

def analyze_sentiment(text):
    try:
        model = get_sentiment_model() 
        result = model(text)[0]
        labels = {'LABEL_0': 'Negative', 'LABEL_1': 'Neutral', 'LABEL_2': 'Positive'}
        return f"{labels.get(result['label'], result['label'])} ({result['score']:.2f})"
    except Exception as e:
        return f"분석 오류: {str(e)}"

def summarize_text(text):
    if not text or len(text.split()) < 10:
        return text 
    
    try:
        model = get_summary_model()
        input_len = len(text.split())
        max_len = min(130, input_len + 10)
        
        result = model(text, max_length=max_len, min_length=10, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        print(f"요약 에러: {e}")
        return text 

def translate_text(text):
    try:
        model = get_translator_model()
        
        # M2M100 모델은 입력 텍스트를 바로 번역합니다.
        # max_length를 넉넉하게 주어 잘림 방지
        result = model(text, max_length=512)
        
        # 'translation_text' 키를 사용하여 결과 반환
        return result[0]['translation_text']
        
    except Exception as e:
        return f"번역 오류: {str(e)}"