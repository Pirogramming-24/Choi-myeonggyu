# apps/posts/services/yolo_service.py
from ultralytics import YOLO
import os

def get_image_tags(image_path):
    try:
        # 1. 모델 로드 (가장 가벼운 yolo11n 사용)
        # 처음 실행 시 자동으로 다운로드됩니다.
        model = YOLO("yolo11n.pt") 
        
        # 2. 이미지 분석 (예측)
        # conf=0.25: 확신이 25% 이상인 것만 태그로 인정
        results = model.predict(image_path, conf=0.25)
        
        detected_tags = set() # 중복 제거를 위해 set 사용
        
        # 3. 결과에서 태그 이름(label) 추출
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0]) # 클래스 ID (예: 0)
                tag_name = model.names[class_id] # 이름 변환 (예: person)
                detected_tags.add(tag_name)
        
        # 리스트로 변환하여 반환
        return list(detected_tags)

    except Exception as e:
        print(f"YOLO 태깅 에러: {e}")
        return []