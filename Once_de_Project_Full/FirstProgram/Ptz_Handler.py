from pynput import keyboard
from onvif import ONVIFCamera
import zeep
import time
from PyQt5.QtWidgets import QMessageBox

class Ptz_Handler:
    def get_position(self,MainWindow, ptz, media_profile):
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
    def make_ptz_handler(self,MainWindow, cmdfile, config):
        mycam = ONVIFCamera(config['ip'], config['port'], config['username'], config['password'])
        # Create media service object
        media = mycam.create_media_service()
        # Create ptz service object
        MainWindow.ptz = mycam.create_ptz_service()

        # Get target profile
        zeep.xsd.simple.AnySimpleType.pythonvalue = self.zeep_pythonvalue
        MainWindow.media_profile = media.GetProfiles()[0]

        # Get PTZ configuration options for getting continuous move range
        request = MainWindow.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = MainWindow.media_profile.PTZConfiguration.token
        ptz_configuration_options = MainWindow.ptz.GetConfigurationOptions(request)

        request = MainWindow.ptz.create_type('ContinuousMove')
        request.ProfileToken = MainWindow.media_profile.token
        MainWindow.ptz.Stop({'ProfileToken': MainWindow.media_profile.token})

        if request.Velocity is None:
            request.Velocity = MainWindow.ptz.GetStatus({'ProfileToken': MainWindow.media_profile.token}).Position
            request.Velocity = MainWindow.ptz.GetStatus({'ProfileToken': MainWindow.media_profile.token}).Position
            request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
            request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

        # Get range of pan and tilt
        # NOTE: X and Y are velocity vector
        MainWindow.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        MainWindow.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        MainWindow.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        MainWindow.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

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
                self.move_up(MainWindow, MainWindow.ptz, request)
                print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                if txt is None:
                    print("^")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "^"))
                    txt.flush()
            if key == "s" or key == "Key.down":  # s
                self.move_down(MainWindow, MainWindow.ptz, request)
                print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                if txt is None:
                    print("v")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "v"))
                    txt.flush()
            if key == "a" or key == "Key.left":  # a
                self.move_left(MainWindow, MainWindow.ptz, request)
                print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                if txt is None:
                    print("<")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "<"))
                    txt.flush()
            if key == "d" or key == "Key.right":  # d
                self.move_right(MainWindow, MainWindow.ptz, request)
                print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                if txt is None:
                    print(">")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, ">"))
                    txt.flush()
            if key == "+":  # p
                self.zoom_up(MainWindow, MainWindow.ptz, request)
                print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                if txt is None:
                    print("+")
                else:
                    txt.write("%.2f\t--\t%s\n" % (t, "+"))
                    txt.flush()
            if key == "-":  # m
                self.zoom_down(MainWindow, MainWindow.ptz, request)
                print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
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
                    self.stop_move(MainWindow, MainWindow.ptz, request)
                    if txt is None:
                        print("x")
                    else:
                        txt.write("%.2f\t--\t%s\n" % (t, "x"))
                        txt.flush()
            # print("* released: " + key)

        listener = keyboard.Listener(on_press=handle_key_press, on_release=handle_key_release)
        listener.start()


    def zeep_pythonvalue(self, xmlvalue):
        return xmlvalue


    def move_up(self, MainWindow, ptz, request):
        request.Velocity.Zoom.x = 0
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = MainWindow.YMAX
        ptz.ContinuousMove(request)


    def move_down(self,MainWindow, ptz, request):
        request.Velocity.Zoom.x = 0
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = MainWindow.YMIN
        ptz.ContinuousMove(request)


    def move_right(self, MainWindow, ptz, request):
        request.Velocity.Zoom.x = 0
        request.Velocity.PanTilt.x = MainWindow.XMAX
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)


    def move_left(self, MainWindow, ptz, request):
        request.Velocity.Zoom.x = 0
        request.Velocity.PanTilt.x = MainWindow.XMIN
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)


    def zoom_up(self, MainWindow, ptz, request):
        request.Velocity.Zoom.x = 1
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)


    def zoom_down(self, MainWindow, ptz, request):
        request.Velocity.Zoom.x = -1
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 0
        ptz.ContinuousMove(request)


    def stop_move(self, MainWindow, ptz, request):
        ptz.Stop({'ProfileToken': request.ProfileToken})

    def displayErrorMessage(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle("Error")
        msgBox.setText(message)
        msgBox.exec_()
