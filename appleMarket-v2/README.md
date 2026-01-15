# 🍎 사과 마켓 (Apple Market) v2

이미지 인식(OCR)을 통한 영양성분 분석 및 YOLO 객체 인식을 통한 상품 해시태그 자동 생성 기능을 포함한 중고거래 플랫폼입니다.

## 🛠️ 개발 환경 및 주의사항 (필독!)

이 프로젝트는 **OCR(PaddleOCR)**과 **객체 인식(YOLO)** 라이브러리를 사용하며, `Numpy` 및 `PyTorch` 버전 호환성이 매우 중요합니다.
**Windows 환경**에서 실행 시 DLL 로드 에러를 방지하기 위해 **Conda 환경** 사용을 강력히 권장합니다.

### ✅ 설치 가이드 (Conda 권장)

채점자님의 PC에서 오류 없이 실행하기 위해 아래 순서대로 설치를 부탁드립니다.

**1. 가상환경 생성 (Python 3.10)**
```bash
conda create -n apple_market python=3.10
conda activate apple_market

2. 핵심 라이브러리 설치 (호환성 버전 고정) 일반 pip install로 설치 시 Windows에서 DLL 오류(WinError 127)가 발생할 수 있어, Conda와 Pip를 혼용하여 설치합니다.

# 1) PyTorch 설치 (Conda 사용 - 시스템 DLL 자동 포함)
conda install pytorch torchvision torchaudio cpuonly -c pytorch -y

# 2) 나머지 라이브러리 설치 (버전 충돌 방지 명령어)
pip install "numpy<2.0" "opencv-python<4.10" "opencv-contrib-python<4.10" "paddlepaddle==2.6.2" "paddleocr>=2.7" ultralytics django Pillow

3. 마이그레이션 및 실행

python manage.py makemigrations
python manage.py migrate
python manage.py runserver

⚠️ 트러블슈팅 (참고사항)
Q. OMP: Error #15: Initializing libiomp5md.dll... 에러가 발생하나요? A. 프로젝트의 manage.py 상단에 이 충돌을 방지하는 코드가 이미 포함되어 있습니다.

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

별도의 설정 없이 바로 실행하시면 됩니다.

✨ 주요 기능
상품 등록/수정/삭제: CRUD 기능 구현 및 Bootstrap UI 적용

영양성분 OCR 분석: 식품 이미지를 업로드하면 칼로리, 탄/단/지 정보를 자동 입력

AI 해시태그 추천: 상품 사진을 업로드하면 YOLO 모델이 사물을 인식해 태그 자동 입력 (AJAX 비동기 처리)

검색 및 필터: 제목 검색, 가격 범위 필터, 해시태그 클릭 시 모아보기 기능