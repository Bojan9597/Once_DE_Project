#
# build to exe without OpenCV:
#    pyinstaller ptz_contorller_app.py --onefile --exclude-module cv2 --add-data="/home/nenad/.pyvenv/lib/python3.8/site-packages/wsdl/*:wsdl/"
#
# (path separator is ; on MS Windows)
#

# taken from <https://github.com/RichardoMrMu/python-onvif>

import os
import sys
import json
import time

from onvif import ONVIFCamera
import zeep
from urllib.parse import urlparse

from pynput.keyboard import Key, Listener, Controller
from pynput import keyboard

try:
	import cv2
except:
	cv2 = None

#
#
#

XMAX = +1
XMIN = -1
YMAX = +1
YMIN = -1

def get_position(ptz, media_profile):
    status = ptz.GetStatus({'ProfileToken': media_profile.token})
    position = status.Position
    return f"Pan: {position.PanTilt.x}  Tilt: {position.PanTilt.y}  Zoom: {position.Zoom.x}"


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


def move_up(ptz, request):
    request.Velocity.Zoom.x = 0
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMAX
    ptz.ContinuousMove(request)


def move_down(ptz, request):
    request.Velocity.Zoom.x = 0
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMIN
    ptz.ContinuousMove(request)


def move_right(ptz, request):
    request.Velocity.Zoom.x = 0
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = 0
    ptz.ContinuousMove(request)


def move_left(ptz, request):
    request.Velocity.Zoom.x = 0
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = 0
    ptz.ContinuousMove(request)


def zoom_up(ptz,request):
    request.Velocity.Zoom.x = 1
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    ptz.ContinuousMove(request)


def zoom_down(ptz,request):
    request.Velocity.Zoom.x = -1
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    ptz.ContinuousMove(request)


def stop_move(ptz, request):
	ptz.Stop({'ProfileToken': request.ProfileToken})


def make_ptz_handler(cmdfile, config):
    mycam = ONVIFCamera(config['ip'], config['port'], config['user'], config['pass'])
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    media_profile = media.GetProfiles()[0]

    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = media_profile.token
    ptz.Stop({'ProfileToken': media_profile.token})

    if request.Velocity is None:
        request.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        request.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
        request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

    # Get range of pan and tilt
    # NOTE: X and Y are velocity vector
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

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
                #print("* pressed: " + key)
        else:
                # the user is holding down the key
                return

        t = time.time() - t0

        if key == "w" or key=="Key.up": # w
            move_up(ptz, request)
            print(get_position(ptz,media_profile))
            if txt is None:
                print("^")
            else:
                txt.write("%.2f\t--\t%s\n" % (t, "^"))
                txt.flush()
        if key == "s" or key=="Key.down": # s
            move_down(ptz, request)
            print(get_position(ptz, media_profile))
            if txt is None:
                print("v")
            else:
                txt.write("%.2f\t--\t%s\n" % (t, "v"))
                txt.flush()
        if key == "a" or key=="Key.left": # a
            move_left(ptz, request)
            print(get_position(ptz, media_profile))
            if txt is None:
                print("<")
            else:
                txt.write("%.2f\t--\t%s\n" % (t, "<"))
                txt.flush()
        if key == "d" or key=="Key.right": # d
            move_right(ptz, request)
            print(get_position(ptz, media_profile))
            if txt is None:
                print(">")
            else:
                txt.write("%.2f\t--\t%s\n" % (t, ">"))
                txt.flush()
        if key == "+": # p
            zoom_up(ptz, request)
            print(get_position(ptz, media_profile))
            if txt is None:
                print("+")
            else:
                txt.write("%.2f\t--\t%s\n" % (t, "+"))
                txt.flush()
        if key == "-": # m
            zoom_down(ptz, request)
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
                    stop_move(ptz, request)
                    if txt is None:
                        print("x")
                    else:
                        txt.write("%.2f\t--\t%s\n" % (t, "x"))
                        txt.flush()
        #print("* released: " + key)

    listener = keyboard.Listener(on_press=handle_key_press, on_release=handle_key_release)
    listener.start()

#
#
#

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

#
#
#

if cv2 is not None:
	def interaction_loop(camurl):
		vcap = cv2.VideoCapture(camurl)

		while True:
			#
			ret, frame = vcap.read()
			if not ret:
				break
			frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
			cv2.imshow("stream", frame)
			#
			key = cv2.waitKey(1)
			if key == ord('q'):
				break

		vcap.release()
		cv2.destroyAllWindows()
else:
	def interaction_loop(camurl):
		for line in sys.stdin.readline():
			if line.strip() == "q":
				break

#
#
#

def main(config):

	if config["saveprefix"] != "":
		make_ptz_handler(config["saveprefix"] + ".txt", config["ptz"])
		p = spawn_ffmpeg_process(config["ffmpeg"], config["cam"], config["saveprefix"] + ".mkv")
	else:
		make_ptz_handler(None, config["ptz"])

	interaction_loop(config["cam"])

	if config["saveprefix"] != "":
		p.stdin.write(b"q")

if __name__ == "__main__":
	if len(sys.argv) == 2:
		with open(sys.argv[1], "r") as fp:
			main(
				json.load(fp)
			)
	else:
		main({
			"cam": "rtsp://admin:once1234!@192.168.100.18:554/Streaming/Channels/101",
			"ptz": {
				"ip": "192.168.100.18",
				"port": 80,
				"user": "admin",
				"pass": "once1234!"
			},
			"ffmpeg": "ffmpeg",
			"saveprefix": "",
		})