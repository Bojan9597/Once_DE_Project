import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
from CoordinatesCalculator import CoordinatesCalculator
from pynput import keyboard
import time
import subprocess
from onvif import ONVIFCamera
import zeep
import traceback
from threading import Thread


class MainWindow(QWidget):
    camera_url_ptz = ""
    camera_url_wa = ""
    saveprefix = ""
    # Camera login information
    XMAX = +1
    XMIN = -1
    YMAX = +1
    YMIN = -1
    ptz = ""
    media_profile = ""
    coordinatesCalculator = CoordinatesCalculator('CoordinatesPTZ.txt', 'CoordinatesWA.txt')
    requestAbsolute = ""
    request = ""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(400, 400, 900, 450)
        self.corespondingX = 0
        self.corespondingY = 0
        # Create labels for displaying video frames and camera names
        self.ptz_label = QLabel("PTZ Camera")
        self.wa_label = QLabel("WA Camera")
        self.left_label = QLabel()
        self.right_label = QLabel()

        # Set the background images for the labels
        ptz_background = QPixmap(
            "C:/Users/bojan/Desktop/Once_DE_Project/Once_DE_Project/FirstProgram/images/ptzCamera.png")
        wa_background = QPixmap(
            "C:/Users/bojan/Desktop/Once_DE_Project/Once_DE_Project/FirstProgram/images/wideAngleCamera.png")
        self.left_label.setPixmap(ptz_background.scaled(self.width() // 2, self.height(), Qt.KeepAspectRatio))
        self.right_label.setPixmap(wa_background.scaled(self.width() // 2, self.height(), Qt.KeepAspectRatio))

        # Create the grid layout for the main window
        grid = QGridLayout()
        self.setLayout(grid)

        # Add labels to the grid layout
        grid.addWidget(self.ptz_label, 0, 0)
        grid.addWidget(self.wa_label, 0, 1)
        grid.addWidget(self.left_label, 1, 0)
        grid.addWidget(self.right_label, 1, 1)

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
        self.handleLogin()

    def handleLogin(self):
        usernamePTZ, usernameWA = "", ""
        passwordPTZ, passwordWA = "", ""
        ip_addressPTZ, ip_addressWA = "", ""
        with open('ConfigurationPTZ.txt', 'r') as f:
            usernamePTZ = f.readline().strip()
            passwordPTZ = f.readline().strip()
            ip_addressPTZ = f.readline().strip()
        self.camera_url_ptz = f"rtsp://{usernamePTZ}:{passwordPTZ}@{ip_addressPTZ}/Streaming/Channels/1"
        self.capturePTZ = cv2.VideoCapture(self.camera_url_ptz)  # Adjust the camera index if necessary
        self.readPTZ = True

        with open('ConfigurationWA.txt', 'r') as f:
            usernameWA = f.readline().strip()
            passwordWA = f.readline().strip()
            ip_addressWA = f.readline().strip()
        self.camera_url_wa = f"rtsp://{usernameWA}:{passwordWA}@{ip_addressWA}/Streaming/Channels/1"
        self.captureWA = cv2.VideoCapture(self.camera_url_wa)
        self.readWA = True
        camera_data = {"ip": ip_addressWA, "port": 80, "username": usernameWA, "password": passwordWA}
        if self.saveprefix != "":
            self.make_ptz_handler(self.saveprefix + ".txt", camera_data)
            # p = spawn_ffmpeg_process(config["ffmpeg"], config["cam"], config["saveprefix"] + ".mkv")
        else:
            self.make_ptz_handler(None, camera_data)

        print(
            f"Login successful for source 1. Username: {usernameWA}, Password: {passwordWA}, IP Address: {ip_addressWA}")
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
                self.add_red_cross(frameWA_rgb)
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
            width_ratio = pos.x() / self.right_label.width()
            height_ratio = pos.y() / self.right_label.height()

            # Get the frame dimensions
            retWA, frameWA = self.capturePTZ.read()
            if retWA:
                frame_height, frame_width, _ = frameWA.shape

                # Calculate the coordinates in the frame
                x = int(width_ratio * frame_width)
                y = int(height_ratio * frame_height)

                # Calculate the coordinates in the frame
                self.corespondingX = x
                self.corespondingY = y
                print(self.corespondingX, self.corespondingY)
                newX, newY = self.coordinatesCalculator.calculate_corresponding_coordinate(x, y)
                print(f"Coordinates in the frame: ({newX}, {newY})")

                # Start a new thread to move to the selected position
                try:
                    move_thread = Thread(target=self.move_to_position,
                                         args=(self.ptz, self.requestAbsolute, newX, newY))
                    move_thread.start()
                except Exception as e:
                    traceback.print_exc()
                    print("An error occurred while starting the move thread.")

    def move_to_position(self, ptz, request, x, y):
        try:
            # set position to x, y
            request.Position.PanTilt.x = x
            request.Position.PanTilt.y = y

            ptz.AbsoluteMove(request)
        except Exception as e:
            print(f"Error moving the camera: {str(e)}")

    def get_position(self, ptz, media_profile):
        # Get the PTZ position using the ONVIF camera
        try:
            # Get the PTZ status from the camera
            status = ptz.GetStatus({'ProfileToken': media_profile.token})

            # Get the position information
            position = status.Position

            # Extract the relevant coordinates and zoom information
            x = position.PanTilt.x
            y = position.PanTilt.y
            zoom = position.Zoom.x

            return x, y, zoom
        except Exception as e:
            print(f"Error retrieving PTZ position: {str(e)}")
            return 0, 0, 0

    def zeep_pythonvalue(self, xmlvalue):
        return xmlvalue

    def move_up(self, ptz, request):
        request.Velocity.Zoom.x = 0
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = self.YMAX
        ptz.ContinuousMove(request)

    def move_down(self, ptz, request):
        request.Velocity.Zoom.x = 0
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = self.YMIN
        ptz.ContinuousMove(request)

    def move_right(self, ptz, request):
        request.Velocity.Zoom.x = 0
        request.Velocity.PanTilt.x = self.XMAX
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)

    def move_left(self, ptz, request):
        request.Velocity.Zoom.x = 0
        request.Velocity.PanTilt.x = self.XMIN
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)

    def zoom_up(self, ptz, request):
        request.Velocity.Zoom.x = 1
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)

    def zoom_down(self, ptz, request):
        request.Velocity.Zoom.x = -1
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)

    def stop_move(self, ptz, request):
        ptz.Stop({'ProfileToken': request.ProfileToken})

    def make_ptz_handler(self, cmdfile, config):
        mycam = ONVIFCamera(config['ip'], config['port'], config['username'], config['password'])
        # Create media service object
        media = mycam.create_media_service()
        # Create ptz service object
        self.ptz = mycam.create_ptz_service()

        # Get target profile
        zeep.xsd.simple.AnySimpleType.pythonvalue = self.zeep_pythonvalue
        self.media_profile = media.GetProfiles()[0]

        # Get PTZ configuration options for getting continuous move range
        self.request = self.ptz.create_type('GetConfigurationOptions')
        self.requestAbsolute = self.ptz.create_type('GetConfigurationOptions')
        self.request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        self.requestAbsolute.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(self.request)
        ptz_configuration_options_absolute = self.ptz.GetConfigurationOptions(self.requestAbsolute)

        self.request = self.ptz.create_type('ContinuousMove')
        self.requestAbsolute = self.ptz.create_type('AbsoluteMove')
        self.request.ProfileToken = self.media_profile.token
        self.requestAbsolute.ProfileToken = self.media_profile.token
        self.ptz.Stop({'ProfileToken': self.media_profile.token})
        self.requestAbsolute.ProfileToken = self.media_profile.token

        if self.request.Velocity is None:
            self.request.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            self.request.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            self.request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
            self.request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI
        if self.requestAbsolute.Position is None:
            self.requestAbsolute.Position = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            self.requestAbsolute.Position.PanTilt.space = \
            ptz_configuration_options_absolute.Spaces.AbsolutePanTiltPositionSpace[0].URI
            self.requestAbsolute.Position.Zoom.space = \
            ptz_configuration_options_absolute.Spaces.AbsoluteZoomPositionSpace[0].URI
        # Get range of pan and tilt
        # NOTE: X and Y are velocity vector
        self.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

        #
        # pressed
        #
        PRESSED = set()
        if cmdfile is None:
            txt = None
        else:
            txt = open(cmdfile, "w")
        t0 = time.time()

        def handle_key_press(key):
            try:
                key = key.char
            except AttributeError:
                key = str(key)

            if key not in PRESSED:
                PRESSED.add(key)
                # print("* pressed: " + key)
            else:
                # the user is holding down the key
                return

            t = time.time() - t0

            if key == "w" or key == "Key.up":  # w
                self.move_up(self.ptz, self.request)
                print(self.get_position(self.ptz, self.media_profile))
                if txt is None:
                    print("^")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "^"))
                    txt.flush()
            if key == "s" or key == "Key.down":  # s
                self.move_down(self.ptz, self.request)
                print(self.get_position(self.ptz, self.media_profile))
                if txt is None:
                    print("v")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "v"))
                    txt.flush()
            if key == "a" or key == "Key.left":  # a
                self.move_left(self.ptz, self.request)
                print(self.get_position(self.ptz, self.media_profile))
                if txt is None:
                    print("<")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "<"))
                    txt.flush()
            if key == "d" or key == "Key.right":  # d
                self.move_right(self.ptz, self.request)
                print(self.get_position(self.ptz, self.media_profile))
                if txt is None:
                    print(">")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, ">"))
                    txt.flush()
            if key == "+":  # p
                self.zoom_up(self.ptz, self.request)
                print(self.get_position(self.ptz, self.media_profile))
                if txt is None:
                    print("+")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "+"))
                    txt.flush()
            if key == "-":  # m
                self.zoom_down(self.ptz, self.request)
                print(self.get_position(self.ptz, self.media_profile))
                if txt is None:
                    print("-")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "-"))
                    txt.flush()

        def handle_key_release(key):
            try:
                key = key.char
            except AttributeError:
                key = str(key)

            t = time.time() - t0

            if key in PRESSED:
                PRESSED.remove(key)
                if len(PRESSED) == 0:
                    self.stop_move(self.ptz, self.request)
                    if txt is None:
                        print("x")
                    else:
                        txt.write("%.2f\t--\t%s\n" % (t, "x"))
                        txt.flush()
            # print("* released: " + key)

        listener = keyboard.Listener(on_press=handle_key_press, on_release=handle_key_release)
        listener.start()

    import subprocess

    def spawn_ffmpeg_process(exe, camurl, savepath):
        cmd = [
            exe,
            "-i", camurl,
            "-vcodec", "copy",
            "-y", savepath
        ]

        ffmpeglog = open("ffmpeg.log", "w")
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=ffmpeglog, stderr=subprocess.STDOUT)
        return p