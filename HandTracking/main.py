import socket
import cv2
import mediapipe as mp
import math
import struct

# Initialize mediapipe hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Open camera
cap = cv2.VideoCapture(0)

# Variables for calibration
calibration_points = []
calibration_step = 0
calibrated = False

# Create socket connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Adjust IP address and port as needed
client_socket.connect(('192.168.1.17', 4747))  

# Calibration function
def calibrate_distance():
    global calibration_step
    global calibration_points
    global calibrated
    
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        return

    # Convert BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process image
    results = hands.process(rgb_frame)

    # Draw instructions
    cv2.putText(frame, "Move your hand as far as possible and press 'f'", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, "Move your hand as close as possible and press 'c'", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Draw hand landmarks if hand is detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for point in hand_landmarks.landmark:
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    # Display output
    cv2.imshow('Hand Tracking', frame)

    key = cv2.waitKey(1)
    if key == ord('f'):
        calibration_points.append(calibration_step)
        calibration_step += 1
    elif key == ord('c'):
        calibration_points.append(calibration_step)
        calibration_step += 1

    if calibration_step >= 2:
        calibrated = True

# Main loop
try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Convert BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process image
        results = hands.process(rgb_frame)

        # Calibration loop
        if not calibrated:
            calibrate_distance()
            continue

        # Send data over socket
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Look between index finger tip landmark 8 and thumb tip landmark 4
                index_finger_tip_landmark = hand_landmarks.landmark[8]
                thumb_tip_landmark = hand_landmarks.landmark[4]

                # Calculate the distance between index finger tip and thumb tip
                distance = math.sqrt((index_finger_tip_landmark.x - thumb_tip_landmark.x)**2 + 
                                     (index_finger_tip_landmark.y - thumb_tip_landmark.y)**2 + 
                                     (index_finger_tip_landmark.z - thumb_tip_landmark.z)**2)

                # Calculate X and Y coordinates on 10x10 grid
                grid_x = min(max(int(thumb_tip_landmark.x * 10), 0), 9)  # Ensure grid_x is between 0 and 9
                grid_y = min(max(int((1 - thumb_tip_landmark.y) * 10), 0), 9)  # Ensure grid_y is between 0 and 9
                
                # Serialize data
                data = struct.pack('fii', distance, grid_x, grid_y)

                # Send data over socket
                client_socket.sendall(data)

        # Display output
        cv2.imshow('Hand Tracking', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print("An error occurred:", e)

finally:
    # Release resources
    client_socket.close()
    cap.release()
    cv2.destroyAllWindows()
