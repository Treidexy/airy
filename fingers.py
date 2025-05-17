import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

def count_fingers(image, results):
    if results.multi_hand_landmarks:
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Get hand landmarks
            landmarks = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append((cx, cy))

            # Define finger tips IDs
            finger_tips_ids = [8, 12, 16, 20]
            count = 0

            # Check if each finger is up
            if landmarks[5][0] < landmarks[17][0]: # Check if thumb is up
                if landmarks[4][0] < landmarks[3][0]:
                    count += 1
            elif landmarks[5][0] > landmarks[17][0]:
                if landmarks[4][0] > landmarks[3][0]:
                    count += 1
            for tip_id in finger_tips_ids:
                if landmarks[tip_id][1] < landmarks[tip_id - 2][1]:
                    count += 1
            # Display the count
            cv2.putText(image, str(count), (50 + hand_idx * 80, 150), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 10)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    count_fingers(image, results)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Finger Counter', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()