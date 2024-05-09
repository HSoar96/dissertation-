import socket
import cv2
import mediapipe as mp
import math
import struct
import numpy as np
import time
from datetime import datetime
import csv

# Initialize mediapipe hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Open camera
cap = cv2.VideoCapture(0)

# Variables for calibration
calibration_points = []
calibration_step = 0
calibrated = False

grid_modifier = 0.8
hex_grid_size = 10

artificial_latency = 0

def create_socket_connection(addr, port):
    # Create socket connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Adjust IP address and port as needed
    client_socket.connect((addr, port))
    return client_socket

def alter_latency(input):
    global artificial_latency
    match int(input):
        case 0:
            artificial_latency = 0
            print(f"Latency set to {artificial_latency}")
            return
        case 1:
            artificial_latency = 30
            print(f"Latency set to {artificial_latency}")
            return
        case 2:
            artificial_latency = 60
            print(f"Latency set to {artificial_latency}")
            return
        case 3:
            artificial_latency = 90
            print(f"Latency set to {artificial_latency}")
            return
        case 4:
            artificial_latency = 120
            print(f"Latency set to {artificial_latency}")
            return
        case 5:
            artificial_latency = 150
            print(f"Latency set to {artificial_latency}")
            return

def draw_hexagon(img, center, size, color, thickness, alpha):
    points = []
    for i in range(6):
          # starting at 30 degrees for flat top hexagon to make it less jaring on the eyes.
        angle_deg = 60 * i + 30
        angle_rad = math.pi / 180 * angle_deg
        point = (int(center[0] + size * math.cos(angle_rad)),
                 int(center[1] + size * math.sin(angle_rad)))
        points.append(point)
    points = np.array(points, np.int32)
    overlay = img.copy()
    cv2.polylines(overlay, [points], isClosed=True, color=color, thickness=thickness)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

def draw_hexagonal_grid(img, grid_size, hex_size):
    h, w = img.shape[:2]
    # Calculate horizontal and vertical space to maintain grid proportions.
    # 80% used to add some padding around the grid.
    horizontal_space = w *grid_modifier
    vertical_space = h * grid_modifier
    start_x = (w - horizontal_space) / 2
    start_y = (h - vertical_space) / 2

    # Draw rows of hexagons
    for row in range(grid_size):
        for col in range(grid_size):
            x = start_x + col * hex_size * math.sqrt(3)
            y = start_y + row * hex_size * 1.5
            if row % 2 == 1:
                # Offset for every second row
                x += hex_size * 0.875
            draw_hexagon(img, (int(x), int(y)), int(hex_size), (0,255,0), 2, 0.25)

def get_hexagon_grid_pos(x,y, img, grid_size, hex_size):
    h, w = img.shape[:2]

    # Calculate the start of the grid based on frame dimensions
    horizontal_space = w * grid_modifier
    vertical_space = h * grid_modifier
    # Hex size removed to ensure its the starting point of the grid not the center
    start_x = (w - horizontal_space) / 2 - (hex_size)
    start_y = (h - vertical_space) / 2 - (hex_size)
    
    # # Adjust x and y relative to the grid start
    x -= start_x
    y -= start_y

    row = int(y // (hex_size * 1.5))
    
    # Adjust column calculation for staggered rows
    if row % 2 == 1:
        # Account for staggered row offset
        x -= hex_size * 0.875
    
    # Calculate column
    col = int(x // (hex_size * math.sqrt(3)))
    
    # Clamp values to ensure they fall within the grid size limits
    col = max(0, min(col, grid_size - 1))
    row = max(0, min(row, grid_size - 1))

    return col, row

def csv_log():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"latency_log_{timestamp}.csv"
    f = open(filename, mode='w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Latency (ms)", "Artifical latency (ms)"])
    return f, writer

def send_data_to_unity(data, client_socket,csv_writer):   
    try:
        # Timestamp before sending
        send_time = time.perf_counter()
        # Waits to send the data to add variable artifical latency
        time.sleep(artificial_latency/1000)
        client_socket.sendall(data)

        # Wait for response
        response = client_socket.recv(1024) 
        receive_time = time.perf_counter()

        # Calculate latency
        latency = receive_time - send_time
        latency_ms = latency * 1000
        # Log to CSV
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        csv_writer.writerow([current_time, f"{latency_ms:.2f}", artificial_latency])

    except Exception as e:
        print("An error occurred:", e)

def main():

    # Setup CSV logging
    file, csv_writer = csv_log()

    client_socket = create_socket_connection('127.0.0.1', 2525)

    # Changes latency and sends it to unity for configuration
    alter_latency(input("Awaiting latency input..."))
    packed_data = struct.pack('<i', artificial_latency)
    client_socket.sendall(packed_data)

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

            # Define hexagon size based on frame width
            hex_size = int((frame.shape[1] * 0.8) / (10 * 1.75))

            # Draw the hexagonal grid
            draw_hexagonal_grid(frame, hex_grid_size, hex_size)

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

                    # Display the distance on the frame
                    cv2.putText(frame, f'Distance: {distance}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    center_x = (index_finger_tip_landmark.x + thumb_tip_landmark.x) / 2 * frame.shape[1]
                    center_y = (thumb_tip_landmark.y + index_finger_tip_landmark.y) / 2 * frame.shape[0]

                    # Draw a dot to show the calculated position.
                    cv2.circle(frame, (int(center_x), int(center_y)), 5, (255, 0, 0), -1)

                    # Get the row and column and print it on screen for the user.
                    col, row = get_hexagon_grid_pos(center_x, center_y, frame, hex_grid_size, hex_size)
                    cv2.putText(frame, f'Grid Position: ({col}, {row})', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    # Serialize data
                    data = struct.pack('fii', distance, col, row)

                    # Send data over socket
                    send_data_to_unity(data, client_socket, csv_writer)

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
        file.close()

if __name__ == "__main__":
    main()