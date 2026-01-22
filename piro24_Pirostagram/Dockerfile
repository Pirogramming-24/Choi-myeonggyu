# 1. 파이썬 3.10 버전 사용 (가장 무난하고 안정적)
FROM python:3.10

# 2. 파이썬 출력 버퍼링 제거 (로그가 바로바로 찍히게 함)
ENV PYTHONUNBUFFERED=1

# 3. 작업 폴더 설정
WORKDIR /app

# 4. 필요한 패키지 리스트 복사 및 설치
# (requirements.txt를 먼저 만들어야 합니다!)
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5. 프로젝트 코드 전체 복사
COPY . /app/

# 6. 서버 실행 명령어 (0.0.0.0으로 열어야 외부 접속 가능)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]