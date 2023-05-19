import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QPixmap
from CoordinatesCalculator import CoordinatesCalculator

class MainWindow(QWidget):
    coordinatesCalculator = CoordinatesCalculator('CoordinatesPTZ.txt', 'CoordinatesWA.txt')
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(400, 400, 1200, 600)
        
        self.corespondingX = 0
        self.corespondingY = 0
        # Create left and right labels for displaying video frames
        self.left_label = QLabel()
        self.right_label = QLabel()

        # Set the background images for the labels
        ptz_background = QPixmap("C:/Users/bojan/Desktop/Once_DE_Project/Once_DE_Project/FirstProgram/images/ptzCamera.png")
        wa_background = QPixmap("C:/Users/bojan/Desktop/Once_DE_Project/Once_DE_Project/FirstProgram/images/wideAngleCamera.png")
        self.left_label.setPixmap(ptz_background.scaled(self.width() // 2, self.height(), Qt.KeepAspectRatio))
        self.right_label.setPixmap(wa_background.scaled(self.width() // 2, self.height(), Qt.KeepAspectRatio))

        # Create the grid layout for the main window
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        self.setLayout(grid)

        # Add labels to the grid layout
        grid.addWidget(self.left_label, 0, 0)
        grid.addWidget(self.right_label, 0, 1)

        # Start capturing video frames
        self.capturePTZ = None
        self.captureWA = None
        self.readPTZ = False
        self.readWA = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_frames)
        self.timer.start(30)  # Set the desired frame update interval (in milliseconds)

        # Enable mouse tracking on the labels
        self.left_label.setMouseTracking(True)
        self.right_label.setMouseTracking(True)

        # Connect mouse press event to the labels
        self.left_label.mousePressEvent = self.left_label_mousePressEvent
        self.right_label.mousePressEvent = self.right_label_mousePressEvent
        self.handleLogin()

    def handleLogin(self):
        usernamePTZ,usernameWA = "",""
        passwordPTZ,passwordWA = "",""
        ip_addressPTZ,ip_addressWA = "",""
        with open('ConfigurationPTZ.txt', 'r') as f:
            usernamePTZ = f.readline().strip()
            passwordPTZ = f.readline().strip()
            ip_addressPTZ = f.readline().strip()
        if usernamePTZ =="admin" and passwordPTZ == "password":
            if self.captureWA is not None:
                self.capturePTZ = self.captureWA
            else:
                self.capturePTZ = cv2.VideoCapture(0)  # Adjust the camera index if necessary
                self.readPTZ = True
                print(f"Login successful for source 1. Username: {usernamePTZ}, Password: {passwordPTZ}, IP Address: {ip_addressPTZ}")

        with open('ConfigurationWA.txt', 'r') as f:
            usernameWA = f.readline().strip()
            passwordWA = f.readline().strip()
            ip_addressWA = f.readline().strip()
        if usernameWA =="admin" and passwordWA == "password":
            if self.capturePTZ is not None:
                self.captureWA = self.capturePTZ
            else:
                self.captureWA = cv2.VideoCapture(0)  # Adjust the camera index if necessary
            self.capturePTZ = self.captureWA
            self.readWA = True
        print(f"Login successful for source 1. Username: {usernameWA}, Password: {passwordWA}, IP Address: {ip_addressWA}")

        print("Login successful! Streaming video...")

    def add_red_cross(self, frame):
        # Get the frame dimensions
        frame_height, frame_width, _ = frame.shape

        # Calculate the center coordinates
        # center_x = frame_width // 2
        # center_y = frame_height // 2
        left_coordinates_x, left_coordinates_y = self.coordinatesCalculator.calculate_corresponding_coordinate(self.corespondingX, self.corespondingY)
        
        # Convert the coordinates to integers
        left_coordinates_x = int(left_coordinates_x)
        left_coordinates_y = int(left_coordinates_y)

        # Define the cross line properties
        color = (0, 0, 255)  # Red color
        thickness = 2
        
        # Draw the cross lines
        cv2.line(frame, (left_coordinates_x - 10, left_coordinates_y), (left_coordinates_x + 10, left_coordinates_y), color, thickness)
        cv2.line(frame, (left_coordinates_x, left_coordinates_y - 10), (left_coordinates_x, left_coordinates_y + 10), color, thickness)


    def update_video_frames(self):
        if self.readPTZ and self.capturePTZ is not None and self.capturePTZ.isOpened():
            retPTZ, framePTZ = self.capturePTZ.read()
            if retPTZ:
                framePTZ_rgb = cv2.cvtColor(framePTZ, cv2.COLOR_BGR2RGB)

                # Add the red cross to the frame
                self.add_red_cross(framePTZ_rgb)

                imagePTZ = QImage(
                    framePTZ_rgb.data,
                    framePTZ_rgb.shape[1],
                    framePTZ_rgb.shape[0],
                    QImage.Format_RGB888
                )
                scaled_imagePTZ = imagePTZ.scaled(
                    self.left_label.width(),
                    self.left_label.height(),
                    Qt.KeepAspectRatio
                )
                self.left_label.setPixmap(QPixmap.fromImage(scaled_imagePTZ))
        if self.readWA and self.captureWA is not None and self.captureWA.isOpened():
            retWA, frameWA = self.captureWA.read()
            if retWA:
                frameWA_rgb = cv2.cvtColor(frameWA, cv2.COLOR_BGR2RGB)
                imageWA = QImage(
                    frameWA_rgb.data,
                    frameWA_rgb.shape[1],
                    frameWA_rgb.shape[0],
                    QImage.Format_RGB888
                )
                scaled_imageWA = imageWA.scaled(
                    self.right_label.width(),
                    self.right_label.height(),
                    Qt.KeepAspectRatio
                )
                self.right_label.setPixmap(QPixmap.fromImage(scaled_imageWA))

    def left_label_mousePressEvent(self, event):
        if self.capturePTZ is not None and self.capturePTZ.isOpened():
            # Get the mouse position relative to the label
            pos = event.pos()
            width_ratio = pos.x() / self.left_label.width()
            height_ratio = pos.y() / self.left_label.height()

            # Get the frame dimensions
            retPTZ, framePTZ = self.capturePTZ.read()
            if retPTZ:
                frame_height, frame_width, _ = framePTZ.shape

                # Calculate the coordinates in the frame
                x = int(width_ratio * frame_width)
                y = int(height_ratio * frame_height)

    def right_label_mousePressEvent(self, event):
        if self.captureWA is not None and self.captureWA.isOpened():
            # Get the mouse position relative to the label
            pos = event.pos()
            width_ratio = pos.x() / self.right_label.width()
            height_ratio = pos.y() / self.right_label.height()

            # Get the frame dimensions
            retWA, frameWA = self.captureWA.read()
            if retWA:
                frame_height, frame_width, _ = frameWA.shape

                # Calculate the coordinates in the frame
                x = int(width_ratio * frame_width)
                y = int(height_ratio * frame_height)
                
                # Calculate the coordinates in the frame
                self.corespondingX = x
                self.corespondingY = y
