import mediapipe as mp
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import os

# 1. Data Collection (Simplified - you'd need to run this multiple times to collect more data)
DATA_DIR = 'gesture_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

num_samples = 1000  # Number of samples to collect per gesture
gestures = ['fist', 'palm']
labels = []
data = []

mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

cv2.waitKey(0)
for gesture_index, gesture_name in enumerate(gestures):
    gesture_path = os.path.join(DATA_DIR, gesture_name)
    if not os.path.exists(gesture_path):
        os.makedirs(gesture_path)
    print(f"Collecting data for: {gesture_name}")

    cv2.waitKey(0)

    count = 0
    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

                landmark_list = []
                for landmark in hand_landmarks.landmark:
                    landmark_list.extend([landmark.x, landmark.y, landmark.z])
                data.append(landmark_list)
                labels.append(gesture_index)
                count += 1
                cv2.putText(frame, f"Collected: {count}/{num_samples}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f"Collecting for: {gesture_name}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow('Hand Tracking', frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()

# Convert data and labels to numpy arrays
data = np.array(data)
labels = np.array(labels)

# 2. Train a Model
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

model = SVC(kernel='linear', C=1.0)  # You can experiment with different models and parameters
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# 3. Integrate with MediaPipe for Real-time Prediction
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_hands.process(frame_rgb)
    predicted_gesture = "Unknown"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

            landmark_list = []
            for landmark in hand_landmarks.landmark:
                landmark_list.extend([landmark.x, landmark.y, landmark.z])

            if landmark_list:
                landmark_array = np.array([landmark_list])
                prediction = model.predict(landmark_array)[0]
                predicted_gesture = gestures[prediction]

    cv2.putText(frame, f"Gesture: {predicted_gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Hand Tracking with Prediction', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()