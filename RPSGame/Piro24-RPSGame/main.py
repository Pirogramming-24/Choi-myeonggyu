import cv2 as cv
import mediapipe as mp
import math
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import visualization  # 제공된 visualization.py 파일 활용

def get_dist(p1, p2):
    """두 점 사이의 유클리드 거리를 계산합니다."""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def classify_rps(landmarks):
    """
    손가락 개수를 기반으로 한 엄격한 판정 로직:
    - 0개: 바위(0)
    - 2개: 가위(2)
    - 5개: 보(1)
    - 1, 3, 4개: None (출력 안 함)
    """
    fingers = []
    
    # 1. 엄지 판정 (엄지 끝(4)과 새끼손가락 뿌리(17) 사이의 거리를 이용 - 가장 정확함)
    # 접었을 때보다 폈을 때 거리가 확실히 멀어집니다.
    is_thumb_open = get_dist(landmarks[4], landmarks[17]) > get_dist(landmarks[3], landmarks[17])
    fingers.append(is_thumb_open)

    # 2. 나머지 네 손가락 판정 (손목(0)에서 팁(8,12,16,20)까지의 거리 비교)
    # 손가락을 펴면 끝마디가 손목에서 멀어지는 원리를 이용합니다. (회전에 강함)
    fingers.append(get_dist(landmarks[8], landmarks[0]) > get_dist(landmarks[6], landmarks[0]))   # 검지
    fingers.append(get_dist(landmarks[12], landmarks[0]) > get_dist(landmarks[10], landmarks[0])) # 중지
    fingers.append(get_dist(landmarks[16], landmarks[0]) > get_dist(landmarks[14], landmarks[0])) # 약지
    fingers.append(get_dist(landmarks[20], landmarks[0]) > get_dist(landmarks[18], landmarks[0])) # 소지

    # 펴진 손가락 개수 확인
    up_count = fingers.count(True)

    # 3. 사용자 요청에 따른 엄격한 판정
    if up_count == 0:
        return 0  # 주먹 (Rock) - 손가락이 하나라도 펴지면 주먹이 아님
    elif up_count == 2:
        return 2  # 가위 (Scissors) - 정확히 2개일 때만 (한국식/일반식 모두 포함)
    elif up_count == 5:
        return 1  # 보 (Paper) - 5개 모두 펴야 함
    
    return None  # 1, 3, 4개인 경우 아무것도 반환하지 않음 (None)

if __name__ == "__main__":
    print("가위바위보 프로그램을 시작합니다. 'q'를 누르면 종료됩니다.")

    # 모델 설정
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        image_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        detection_result = detector.detect(mp_image)

        if detection_result.hand_landmarks:
            # 랜드마크 시각화
            frame = visualization.draw_manual(frame, detection_result)
            
            # 판정 및 결과 출력
            rps_idx = classify_rps(detection_result.hand_landmarks[0])
            frame = visualization.print_RSP_result(frame, rps_idx)

        cv.imshow('Strict RPS Game', frame)
        if cv.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv.destroyAllWindows()