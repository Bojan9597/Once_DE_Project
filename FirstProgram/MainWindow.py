import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSlot

class MainWindow(QWidget):
    coordinatesPTZ = []
    coordinatesWA = []
    # Camera login information
    camera_ip_ptz = '192.168.100.17'
    username_ptz = 'admin'
    password_ptz = 'once1234!'
    camera_url_ptz = f"rtsp://{username_ptz}:{password_ptz}@{camera_ip_ptz}/Streaming/Channels/1"

    camera_ip_wa = '192.168.100.18'
    username_wa = 'admin'
    password_wa = 'once1234!'
    camera_url_wa = f"rtsp://{username_wa}:{password_wa}@{camera_ip_wa}/Streaming/Channels/1"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(200, 200, 1200, 600)

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
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        self.setLayout(grid)

        # Create PTZ coordinates labels and textboxes
        ptz_coordinates_label = QLabel("PTZ Coordinates")
        ptz_coordinates_label.setFont(QFont("Arial", 16, QFont.Bold))
        x1_label = QLabel("x1, y1:")
        x1_textbox = QLineEdit()
        x2_label = QLabel("x2, y2:")
        x2_textbox = QLineEdit()
        x3_label = QLabel("x3, y3:")
        x3_textbox = QLineEdit()
        x4_label = QLabel("x4, y4:")
        x4_textbox = QLineEdit()

        # Add labels and textboxes for PTZ coordinates to the grid layout
        grid.addWidget(ptz_coordinates_label, 0, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(x1_label, 1, 0)
        grid.addWidget(x1_textbox, 1, 1)
        grid.addWidget(x2_label, 2, 0)
        grid.addWidget(x2_textbox, 2, 1)
        grid.addWidget(x3_label, 3, 0)
        grid.addWidget(x3_textbox, 3, 1)
        grid.addWidget(x4_label, 4, 0)
        grid.addWidget(x4_textbox, 4, 1)

        # Create WA coordinates labels and textboxes
        wa_coordinates_label = QLabel("WA Coordinates")
        wa_coordinates_label.setFont(QFont("Arial", 16, QFont.Bold))
        x1_wa_label = QLabel("x1, y1:")
        x1_wa_textbox = QLineEdit()
        x2_wa_label = QLabel("x2, y2:")
        x2_wa_textbox = QLineEdit()
        x3_wa_label = QLabel("x3, y3:")
        x3_wa_textbox = QLineEdit()
        x4_wa_label = QLabel("x4, y4:")
        x4_wa_textbox = QLineEdit()

        # Add labels and textboxes for WA coordinates to the grid layout
        grid.addWidget(wa_coordinates_label, 0, 2, 1, 2, Qt.AlignCenter)
        grid.addWidget(x1_wa_label, 1, 2)
        grid.addWidget(x1_wa_textbox, 1, 3)
        grid.addWidget(x2_wa_label, 2, 2)
        grid.addWidget(x2_wa_textbox, 2, 3)
        grid.addWidget(x3_wa_label, 3, 2)
        grid.addWidget(x3_wa_textbox, 3, 3)
        grid.addWidget(x4_wa_label, 4, 2)
        grid.addWidget(x4_wa_textbox, 4, 3)

        # Add labels and frame to the grid layout
        grid.addWidget(self.left_label, 5, 0, 1, 2)
        grid.addWidget(self.right_label, 5, 2, 1, 2)


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

    @pyqtSlot(str, str, str, str)
    def handleLogin(self, source, username, password, ip_address):
        if source == "1":

            self.capturePTZ = cv2.VideoCapture(self.camera_url_ptz)  # Adjust the camera index if necessary
            self.readPTZ = True
            print(f"Login successful for source 1. Username: {username}, Password: {password}, IP Address: {ip_address}")
            with open("ConfigurationPTZ.txt", "w") as f:
                f.write(f"{username}\n")
                f.write(f"{password}\n")
                f.write(f"{ip_address}\n")

        elif source == "2":
            self.captureWA = cv2.VideoCapture(self.camera_url_wa)  # Adjust the camera index if necessary
            self.readWA = True
            print(f"Login successful for source 1. Username: {username}, Password: {password}, IP Address: {ip_address}")
            with open("ConfigurationWA.txt", "w") as f:
                f.write(f"{username}\n")
                f.write(f"{password}\n")
                f.write(f"{ip_address}\n")
        print("Login successful! Streaming video...")

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
        cv2.line(frame, (center_x, center_y - 10), (center_x, center_y + 10), color, thickness)

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
                if len(self.coordinatesPTZ) < 4:
                    frame_height, frame_width, _ = framePTZ.shape

                    # Calculate the coordinates in the frame
                    x = int(width_ratio * frame_width)
                    y = int(height_ratio * frame_height)
                    print(x,y)
                    self.coordinatesPTZ.append((x, y))
                # Write the coordinates to the file
                if len(self.coordinatesPTZ) == 4:
                    with open("CoordinatesPTZ.txt", "w") as file:
                        file.write(f"X: {self.coordinatesPTZ[0][0]}, Y: {self.coordinatesPTZ[0][1]}  \n")
                        file.write(f"X: {self.coordinatesPTZ[1][0]}, Y: {self.coordinatesPTZ[1][1]}  \n")
                        file.write(f"X: {self.coordinatesPTZ[2][0]}, Y: {self.coordinatesPTZ[2][1]}  \n")
                        file.write(f"X: {self.coordinatesPTZ[3][0]}, Y: {self.coordinatesPTZ[3][1]}  \n")
            
            # Update the PTZ coordinates labels
            self.update_ptz_coordinates_labels()

    def right_label_mousePressEvent(self, event):
        if self.captureWA is not None and self.captureWA.isOpened():
            # Get the mouse position relative to the label
            pos = event.pos()
            width_ratio = pos.x() / self.right_label.width()
            height_ratio = pos.y() / self.right_label.height()

            # Get the frame dimensions
            retWA, frameWA = self.captureWA.read()
            if retWA:
                if len(self.coordinatesWA) < 4:
                    frame_height, frame_width, _ = frameWA.shape

                    # Calculate the coordinates in the frame
                    x = int(width_ratio * frame_width)
                    y = int(height_ratio * frame_height)
                    print(x,y)
                    self.coordinatesWA.append((x, y))
                # Write the coordinates to the file
                if len(self.coordinatesWA) == 4:
                    with open("CoordinatesWA.txt", "w") as file:
                        file.write(f"X: {self.coordinatesWA[0][0]}, Y: {self.coordinatesWA[0][1]}  \n")
                        file.write(f"X: {self.coordinatesWA[1][0]}, Y: {self.coordinatesWA[1][1]}  \n")
                        file.write(f"X: {self.coordinatesWA[2][0]}, Y: {self.coordinatesWA[2][1]}  \n")
                        file.write(f"X: {self.coordinatesWA[3][0]}, Y: {self.coordinatesWA[3][1]}  \n")
        
        # Update the WA coordinates labels
        self.update_wa_coordinates_labels()
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_U:  # 'u' key
            if self.coordinatesPTZ:
                self.coordinatesPTZ.pop()
            if self.coordinatesWA:
                self.coordinatesWA.pop()
            print("Last coordinate removed.")
        elif key == Qt.Key_E:  # 'e' key
            self.coordinatesPTZ = []
            self.coordinatesWA = []
            print("Coordinates emptied.")
    def update_ptz_coordinates_labels(self):
        # Get the coordinates
        coordinates = self.coordinatesPTZ

        # Get the textboxes for PTZ coordinates
        x1_textbox = self.layout().itemAtPosition(1, 1).widget()
        x2_textbox = self.layout().itemAtPosition(2, 1).widget()
        x3_textbox = self.layout().itemAtPosition(3, 1).widget()
        x4_textbox = self.layout().itemAtPosition(4, 1).widget()

        # Update the text labels if the coordinates exist
        if len(coordinates) >= 1:
            x1_textbox.setText(f"{coordinates[0][0]}, {coordinates[0][1]}")
        if len(coordinates) >= 2:
            x2_textbox.setText(f"{coordinates[1][0]}, {coordinates[1][1]}")
        if len(coordinates) >= 3:
            x3_textbox.setText(f"{coordinates[2][0]}, {coordinates[2][1]}")
        if len(coordinates) >= 4:
            x4_textbox.setText(f"{coordinates[3][0]}, {coordinates[3][1]}")
    def update_wa_coordinates_labels(self):
        # Get the coordinates
        coordinates = self.coordinatesWA
        # Get the textboxes for WA coordinates
        x1_wa_textbox = self.layout().itemAtPosition(1, 3).widget()
        x2_wa_textbox = self.layout().itemAtPosition(2, 3).widget()
        x3_wa_textbox = self.layout().itemAtPosition(3, 3).widget()
        x4_wa_textbox = self.layout().itemAtPosition(4, 3).widget()
        # Update the text labels if the coordinates exist
        if len(coordinates) >= 1:
            x1_wa_textbox.setText(f"{coordinates[0][0]}, {coordinates[0][1]}")
        if len(coordinates) >= 2:
            x2_wa_textbox.setText(f"{coordinates[1][0]}, {coordinates[1][1]}")
        if len(coordinates) >= 3:
            x3_wa_textbox.setText(f"{coordinates[2][0]}, {coordinates[2][1]}")
        if len(coordinates) >= 4:
            x4_wa_textbox.setText(f"{coordinates[3][0]}, {coordinates[3][1]}")