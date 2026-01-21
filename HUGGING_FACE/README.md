# 나만의 AI 사이트 (Django AI Hub)

Django와 Hugging Face Transformers 라이브러리를 활용하여 3가지 이상의 AI 모델을 웹 서비스 형태로 제공하는 프로젝트입니다.

사용자 경험을 고려하여 **탭(Tab) UI**를 적용했으며, **로그인 여부에 따른 접근 제한(Access Control)** 기능을 구현했습니다.

---

## 🛠 사용 모델 (Models)

본 프로젝트는 실습 금지 모델을 사용하지 않고, 성능과 로컬 구동 효율성을 고려하여 아래의 대체 모델들을 선정했습니다.

### 1. cardiffnlp/twitter-roberta-base-sentiment

* **태스크**: Sentiment Analysis (감정 분석)
* **선정 이유**: `distilbert` 보다 트위터 데이터 등 구어체 분석에 강점이 있어 선정
* **입력 예시**: `I really enjoyed learning Django today!`
* **출력 예시**: `Positive (0.98)`

### 2. sshleifer/distilbart-cnn-12-6

* **태스크**: Summarization (요약)
* **선정 이유**: `bart-large-cnn`의 경량화 버전으로, 로컬 환경에서 빠른 추론이 가능하여 선정
* **입력 예시**:
Trump doubles down on Greenland ahead of Davos visit, saying there is 'no going back' 28 minutes ago US President Donald Trump has doubled down on his threats to take control of Greenland, saying there is "no going back". Asked at a news conference how far he was willing to go to acquire the semi-autonomous Danish territory, he replied: "You'll find out." It comes after French President Emmanuel Macron warned of a "shift towards a world without rules", and Canadian Prime Minister Mark Carney said the "old order is not coming back". Trump was due to arrive in Davos ahead of his speech at the World Economic Forum on Wednesday, but a minor electrical issue on Air Force One forced the plane to turn around. It was unclear how the delay would impact his schedule. The White House said the plane turned around and that Trump would fly to Switzerland on another aircraft. Trump has said there are "a lot of meetings scheduled on Greenland". Earlier, during a lengthy press briefing, Trump also told reporters that "things are going to work out pretty well" in Greenland. Asked by the BBC whether the possible break up of Nato was a price he was willing to pay for Greenland, Trump responded: "Nobody has done more for Nato than I have, in every way. "Nato is going to be happy and we are going to be happy [...] We need it for world security." But he earlier questioned whether Nato would come to aid of the US, should it be required. "I know we'll come to [Nato's] rescue, but I just really do question whether or not they'll come to ours," he told reporters. Nato currently has 32 member states, with the US one of the 12 founding countries. Designed to safeguard freedom and security through a collective defence, one of the core principles of the Nato alliance is outlined in Article 5, which says that an armed attack against one or more members will be considered an attack against all. Trump has not ruled out using military force to acquire Greenland. Asked by NBC News on Tuesday whether he would use force to seize the territory, the president replied: "No comment". In an interview with BBC Newsnight on Tuesday, Greenland's minister of industry and natural resources, Naaja Nathanielsen, said that Greenlanders were "bewildered" by the president's demands. "We do not want to be Americans, and we have been quite clear about that," Nathanielsen said. "What value do you put on our culture and our right to decide what happens with us in the future?" Ahead of the World Economic Forum meeting in Davos, Switzerland, Trump shared screenshots that he says showed text messages sent to him by Macron and Nato Secretary General Mark Rutte. In the messages, Rutte was seen saying he was committed to finding a way forward on Greenland, while Macron said he "does not understand what you are doing", but offered to organise a meeting with other leaders in Paris. European Commission President Ursula von der Leyen, addressed the matter directly in a speech to attendees on Tuesday, emphasising that Europe is "fully committed" when it comes to the security of the Arctic.
* **출력 예시**: Trump doubles down on Greenland ahead of Davos visit, saying there is 'no going back' It comes after French President Emmanuel Macron warned of a "shift towards a world without rules" Canadian Prime Minister Mark Carney said the "old order is not coming back"

### 3. facebook/m2m100_418M

* **태스크**: Translation (번역)
* **선정 이유**: 과제 금지 모델인 `NLLB`와 `Helsinki-NLP`를 대체하기 위해 선정. Facebook의 다국어 번역 모델(418M 파라미터) 사용.
* **입력 예시**: `The future of AI is exciting.`
* **출력 예시**: `AI의 미래는 흥미진진합니다.`

---

## 🔥 챌린지 과제: 복합 기능 (Combo)

**파이프라인(Pipeline)** 구조를 활용하여 두 개의 모델을 순차적으로 연결했습니다.

* **기능**: **[요약]** → **[번역]**
* **프로세스**:
1. 사용자가 긴 영어 텍스트를 입력
2. **DistilBART** 모델이 내용을 요약
3. 요약된 내용을 **M2M100** 모델이 한국어로 번역
4. 최종적으로 "요약문(영어)"와 "번역문(한글)"을 동시에 출력


* **추가 기능**: 결과 화면에서 **"같은 내용으로 재생성"** 버튼 제공

---

## 🔐 로그인 제한 (Access Control)

Django의 인증 시스템과 커스텀 데코레이터 로직을 활용하여 보안을 강화했습니다.

1. **공개 탭 (비로그인 허용)**
* `/sentiment` (감정 분석)
* 누구나 접속 및 사용 가능


2. **제한 탭 (로그인 필요)**
* `/summary`, `/translation`, `/combo`
* 비로그인 접근 시: `alert("로그인 후 이용해주세요")` 출력
* 로그인 페이지로 자동 이동 (`?next=` 파라미터 유지)
* 로그인 성공 시 **원래 가려던 페이지로 자동 복귀**


3. **데이터 관리**
* **로그인 유저**: 모든 대화 내역(Input/Output)을 데이터베이스(`AIHistory`)에 저장
* **비로그인 유저**: 세션/컨텍스트 휘발성 처리 (새로고침 시 초기화)



---

## 🚀 실행 방법 (How to Run)

### 1. 환경 설정 및 설치

```bash
# 가상환경 활성화
source venv/Scripts/activate  # (Windows Git Bash)

# 필수 패키지 설치 (sentencepiece 포함 필수)
pip install django transformers torch requests python-dotenv pillow sentencepiece

```

### 2. 데이터베이스 마이그레이션

```bash
python manage.py makemigrations
python manage.py migrate

```

### 3. 관리자 계정 생성 (테스트용)

```bash
python manage.py createsuperuser

```

### 4. 서버 실행

```bash
python manage.py runserver

```

*최초 실행 시 모델 다운로드(약 2~3GB)로 인해 시간이 소요될 수 있습니다.*

---

## ✅ 구현 체크리스트

### 기본 요구사항

* [x] 탭 3개 이상 + 각 탭 별 URL 분리 (`/sentiment`, `/summary`, `/translation`)
* [x] 각 탭: 입력 → 실행 → 결과 출력 구조 구현
* [x] 에러 처리: 모델 호출 실패/입력 오류 시 `messages` 프레임워크로 알림
* [x] 로딩 표시: 터미널 로그를 통해 다운로드 및 로딩 상태 확인 가능, 사이트 내에서도 구현 성공
* [x] 요청 히스토리: 화면 하단에 최근 5개 기록 출력
* [x] `.env` 사용: API Key 등 환경변수 분리 (코드 내 하드코딩 지양)

### 로그인 제한 체크

* [x] 비로그인 사용자는 1개 탭(`Sentiment`)만 접근 가능
* [x] 제한 탭 접근 시 alert 후 로그인 페이지로 redirect
* [x] 로그인 성공 시 원래 페이지로 복귀(`next` 처리)

### 챌린지 과제

* [x] 복합 모델 페이지 추가 (`/combo`)
* [x] 파이프라인 연결 (Summarization + Translation)
* [x] 재생성 버튼 구현