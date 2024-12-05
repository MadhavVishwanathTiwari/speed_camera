import time
import math
import datetime
import cv2
import numpy as np
from picamera2 import Picamera2
import logging
from utils import get_speed, secs_diff, record_speed  # Import utility functions

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    # Print roll number initially
    ROLL_NUMBER = "231031010"
    print(f"My Roll Number: {ROLL_NUMBER}")

    # Constants
    DISTANCE = 76  # Distance to road in feet
    MIN_SPEED = 0  # Minimum speed for saving images
    SAVE_CSV = False  # Enable saving speed data to CSV
    THRESHOLD = 15
    MIN_AREA = 175
    BLURSIZE = (15, 15)
    RESOLUTION = (640, 480)  # (width, height)
    FOV = 53.5  # Field of view in degrees
    FPS = 30
    SHOW_BOUNDS = True
    SHOW_IMAGE = True

    WAITING, TRACKING, SAVING = 0, 1, 2
    UNKNOWN, LEFT_TO_RIGHT, RIGHT_TO_LEFT = 0, 1, 2

    # Initialize variables for drawing
    drawing = False
    ix, iy, fx, fy = -1, -1, -1, -1
    setup_complete = False

    # Define monitored area
    def draw_rectangle(event, x, y, flags, param):
        """Mouse callback function for drawing capture area."""
        global ix, iy, fx, fy, drawing, setup_complete, image, org_image, prompt

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                image = org_image.copy()
                prompt_on_image(image, prompt)
                cv2.rectangle(image, (ix, iy), (x, y), (0, 255, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            fx, fy = x, y
            image = org_image.copy()
            prompt_on_image(image, prompt)
            cv2.rectangle(image, (ix, iy), (fx, fy), (0, 255, 0), 2)

    def prompt_on_image(img, txt):
        """Place a prompt on the displayed image."""
        cv2.putText(img, txt, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # Initialize camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": RESOLUTION}))
    picam2.start()

    # Allow the camera to warm up
    time.sleep(2)

    # Create image window
    cv2.namedWindow("Speed Camera")
    cv2.setMouseCallback("Speed Camera", draw_rectangle)

    # Prompt for defining monitored area
    image = picam2.capture_array()
    org_image = image.copy()
    prompt = "Define the monitored area - press 'c' to continue"
    prompt_on_image(image, prompt)

    while True:
        cv2.imshow("Speed Camera", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            break
    # Normalize coordinates
    upper_left_x, lower_right_x = (ix, fx) if ix < fx else (fx, ix)
    upper_left_y, lower_right_y = (iy, fy) if iy < fy else (fy, iy)

    monitored_width = lower_right_x - upper_left_x
    monitored_height = lower_right_y - upper_left_y
    frame_width_ft = 2 * (math.tan(math.radians(FOV * 0.5)) * DISTANCE)
    ftperpixel = frame_width_ft / RESOLUTION[0]

    logging.info(f"Monitored Area: {monitored_width * monitored_height} pixels")

    # Main loop
    base_image = None
    state = WAITING
    direction = UNKNOWN
    initial_x, last_x = 0, 0

    while True:
        frame = picam2.capture_array()
        timestamp = datetime.datetime.now()

        cropped_image = frame[upper_left_y:lower_right_y, upper_left_x:lower_right_x]
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, BLURSIZE, 0)

        if base_image is None:
            base_image = gray.copy().astype("float")
            continue

        frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(base_image))
        _, thresh = cv2.threshold(frame_delta, THRESHOLD, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours
        motion_found, biggest_area = False, 0
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            found_area = w * h
            if found_area > MIN_AREA and found_area > biggest_area:
                biggest_area = found_area
                motion_found = True

        # Handle tracking
        if motion_found:
            if state == WAITING:
                state = TRACKING
                initial_x = x
                initial_time = timestamp
            elif state == TRACKING:
                secs = secs_diff(timestamp, initial_time)
                if secs > 0.5:
                    mph = get_speed(abs(x - initial_x), ftperpixel, secs)
                    logging.info(f"Speed: {mph:.2f} mph")
        else:
            state = WAITING

        # Update display
        if SHOW_IMAGE:
            cv2.imshow("Speed Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
