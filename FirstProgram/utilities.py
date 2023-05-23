import cv2

def add_red_cross(self, frame):
    # Get the frame dimensions
    frame_height, frame_width, _ = frame.shape
    # Calculate the center coordinates
    center_x = frame_width // 2
    center_y = frame_height // 2
    # Define the cross line properties
    color = (0, 0, 255)  # Red color
    thickness = 2
    # Draw the cross lines
    cv2.line(frame, (center_x - 10, center_y), (center_x + 10, center_y), color, thickness)