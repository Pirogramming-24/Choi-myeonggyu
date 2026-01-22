# ==========================================
# 1. 빌드(Builder) 단계
# ==========================================
FROM python:3.10-slim AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 파이썬 관련 환경 변수 (pyc 파일 생성 금지, 버퍼링 비활성화)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Pillow 등 라이브러리 설치를 위한 시스템 패키지 설치
# (설치 후 캐시 삭제로 용량 절약)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# 패키지 목록 복사 및 설치 (wheels 형태로 변환하여 저장)
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ==========================================
# 2. 실행(Runtime) 단계 (최종 이미지)
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# 런타임에서도 Pillow 작동을 위해 최소한의 라이브러리는 필요할 수 있음 (보통 slim에 포함되나 안전하게)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g && \
    rm -rf /var/lib/apt/lists/*

# Builder 단계에서 만든 가벼운 설치 파일들만 가져오기
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 가져온 파일로 라이브러리 설치 후 설치 파일 삭제
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# 프로젝트 코드 복사 (.dockerignore에 정의된 파일 제외)
COPY . .

# 실행 명령어 (마이그레이션 -> 데이터로딩 -> 서버실행)
# 주의: loaddata는 fixture 파일이 있을 때만 작동합니다. 없으면 빼세요.
CMD sh -c "python manage.py makemigrations --noinput && \
           python manage.py migrate --noinput && \
           python manage.py runserver 0.0.0.0:8000"# ==========================================
# 1. 빌드(Builder) 단계
# ==========================================
FROM python:3.10-slim AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 파이썬 관련 환경 변수 (pyc 파일 생성 금지, 버퍼링 비활성화)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Pillow 등 라이브러리 설치를 위한 시스템 패키지 설치
# (설치 후 캐시 삭제로 용량 절약)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# 패키지 목록 복사 및 설치 (wheels 형태로 변환하여 저장)
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ==========================================
# 2. 실행(Runtime) 단계 (최종 이미지)
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# 런타임에서도 Pillow 작동을 위해 최소한의 라이브러리는 필요할 수 있음 (보통 slim에 포함되나 안전하게)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g && \
    rm -rf /var/lib/apt/lists/*

# Builder 단계에서 만든 가벼운 설치 파일들만 가져오기
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 가져온 파일로 라이브러리 설치 후 설치 파일 삭제
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# 프로젝트 코드 복사 (.dockerignore에 정의된 파일 제외)
COPY . .

# 실행 명령어 (마이그레이션 -> 데이터로딩 -> 서버실행)
# 주의: loaddata는 fixture 파일이 있을 때만 작동합니다. 없으면 빼세요.
CMD sh -c "python manage.py makemigrations --noinput && \
           python manage.py migrate --noinput && \
           python manage.py runserver 0.0.0.0:8000"