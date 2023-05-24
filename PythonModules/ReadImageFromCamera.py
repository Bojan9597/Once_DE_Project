import cv2
import PyQt5

# Open a video capture object
cap = cv2.VideoCapture(0)

# Create a window to display the video stream
cv2.namedWindow('Video Stream')

# Define a mouse callback function
def mouse_callback(event, x, y, flags, param):
    # If left button is clicked, save the coordinates to file
    if event == cv2.EVENT_LBUTTONDOWN:
        with open('coordinates.txt', 'a') as f:
            f.write('{}, {}\n'.format(x, y))

# Set the mouse callback function for the window
cv2.setMouseCallback('Video Stream', mouse_callback)

# Loop through the video frames
while True:
    # Read a frame from the video stream
    ret, frame = cap.read()

    # If the frame was not read successfully, break out of the loop
    if not ret:
        break

    # Display the frame in the window
    cv2.imshow('Video Stream', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release the video capture object and close the window
cap.release()
cv2.destroyAllWindows()
