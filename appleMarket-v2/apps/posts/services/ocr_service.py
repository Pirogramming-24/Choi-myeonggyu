import os
import cv2
import numpy as np
from paddleocr import PaddleOCR

# 전역 OCR 객체 (한 번만 초기화)
_ocr_instance = None

def get_ocr_instance():
    """OCR 인스턴스 싱글톤"""
    global _ocr_instance
    if _ocr_instance is None:
        try:
            _ocr_instance = PaddleOCR(
                use_angle_cls=True,
                lang='korean',
                use_gpu=False,
                show_log=False  # 로그 최소화
            )
        except:
            _ocr_instance = PaddleOCR(use_angle_cls=True, lang='ko', show_log=False)
    return _ocr_instance

def simple_preprocess(image_path):
    """
    간단한 전처리 (과도하지 않게)
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        
        # 1. 작으면 확대
        h, w = img.shape
        if h < 400:
            scale = 400 / h
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # 2. 대비 강화
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img)
        
        return enhanced
    except Exception as e:
        print(f"⚠️ 전처리 실패: {e}")
        return None

def extract_texts_from_result(ocr_result):
    """
    PaddleOCR 결과에서 텍스트만 추출
    """
    texts = []
    if ocr_result and ocr_result[0]:
        for line in ocr_result[0]:
            text = line[1][0]
            confidence = line[1][1]
            texts.append(text)
            print(f"  - {text} (신뢰도: {confidence:.2%})")
    return texts

def get_ocr_result(image_path):
    """
    메인 OCR 함수 (듀얼 모드)
    
    Args:
        image_path (str): 이미지 파일 경로
    
    Returns:
        list: 추출된 텍스트 리스트 ['영양정보', '130 kcal', ...]
    """
    
    print("\n" + "="*60)
    print(f"📸 OCR 시작: {os.path.basename(image_path)}")
    print("="*60)
    
    # 파일 존재 확인
    if not os.path.exists(image_path):
        print(f"❌ 파일 없음: {image_path}")
        return []
    
    ocr = get_ocr_instance()
    
    # ===== 방법 1: 원본 =====
    print("\n[방법 1] 원본 이미지")
    print("-"*60)
    try:
        result1 = ocr.ocr(image_path, cls=True)
        texts1 = extract_texts_from_result(result1)
        print(f"✅ {len(texts1)}개 텍스트 추출")
    except Exception as e:
        print(f"❌ 실패: {e}")
        texts1 = []
    
    # ===== 방법 2: 전처리 =====
    print("\n[방법 2] 전처리 이미지")
    print("-"*60)
    
    temp_path = None
    try:
        processed = simple_preprocess(image_path)
        
        if processed is not None:
            # 임시 파일 저장
            dir_name = os.path.dirname(image_path)
            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            temp_path = os.path.join(dir_name, f"{name}_temp{ext}")
            
            cv2.imwrite(temp_path, processed)
            
            result2 = ocr.ocr(temp_path, cls=True)
            texts2 = extract_texts_from_result(result2)
            print(f"✅ {len(texts2)}개 텍스트 추출")
        else:
            texts2 = []
    except Exception as e:
        print(f"❌ 실패: {e}")
        texts2 = []
    finally:
        # 임시 파일 삭제
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

    
    
    # ===== 결과 선택 =====
    print("\n" + "="*60)
    if len(texts2) > len(texts1):
        print(f"✅ 전처리 결과 채택 ({len(texts2)}개)")
        final_texts = texts2
    else:
        print(f"✅ 원본 결과 채택 ({len(texts1)}개)")
        final_texts = texts1
    
    print("="*60 + "\n")
    
    return final_texts
