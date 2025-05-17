import cv2

import process
import config

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    print("Starting webcam feed. Press 'ESC' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print('Error: Failed to grab frame.')
            break

        frame = cv2.flip(frame, 1)
        process.recognize(frame)

        if config.SHOW_WINDOW:
            display_frame = frame.copy();
            process.draw_hands(display_frame)
            # display_frame= cv2.flip(display_frame, 1)
            process.draw_ui(display_frame)

            cv2.imshow('Airy Hand Magic', display_frame)
        if cv2.waitKey(5) & 0xFF == 27:
            print('Exiting...')
            break
    cap.release()
    cv2.destroyAllWindows()

    
if __name__ == '__main__':
    main()