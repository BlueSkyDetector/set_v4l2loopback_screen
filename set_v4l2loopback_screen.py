#!/usr/bin/env python
from Xlib import display
import array
import glob
import fcntl
import argparse
import subprocess
import sys
import signal


ffmpeg_proc = None


class Screen(object):
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return "Screen(x=%d, y=%d, width=%d, height=%d)" % (self.x, self.y, self.width, self.height)

    def __repr__(self):
        return "Screen(x=%d, y=%d, width=%d, height=%d)" % (self.x, self.y, self.width, self.height)


def get_screens_size():
    screens = list()
    d = display.Display()
    if not d.has_extension('XINERAMA'):
        return None
    d.xinerama_query_screens()
    xinerama_screens = d.xinerama_query_screens()
    for screen_data in xinerama_screens._data['screens']:
        screens.append(Screen(screen_data['x'],
                              screen_data['y'],
                              screen_data['width'],
                              screen_data['height'],
                              )
                       )
    return screens


def get_v4l2loopback_dev():
    v4l2_devs = glob.glob("/dev/video*")
    for v4l2_dev in v4l2_devs:
        v4l2_fd = open(v4l2_dev, "rb")
        buf_drv = array.array('b', (' ' * 16).encode())
        # 2154321408 means VIDIOC_QUERYCAP defined in videodev2.h
        res = fcntl.ioctl(v4l2_fd, 2154321408, buf_drv)
        if res == 0:
            drv_name = buf_drv.tostring().decode().replace('\x00', '')
            if drv_name == 'v4l2 loopback':
                v4l2_fd.close()
                return v4l2_dev
        v4l2_fd.close()
    return None


def send_signal(signum, frame):
    ffmpeg_proc.send_signal(signal.SIGINT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',
                        '--screen',
                        action='store',
                        required=True,
                        type=int,
                        default=False,
                        help='Set screen number to loopback to v4l2 device')
    parser.add_argument('-r',
                        '--reload_v4l2loopback',
                        action='store_true',
                        default=False,
                        help='Set if v4l2loopback module reloading is needed (root permission is required)')
    args = parser.parse_args()
    screens = get_screens_size()
    if args.screen > len(screens):
        sys.exit(1)
    if args.reload_v4l2loopback:
        if subprocess.call(['modprobe', '-r', 'v4l2loopback']) or subprocess.call(['modprobe', 'v4l2loopback', 'exclusive_caps=1']):
            print('v4l2loopback looks not installed')
            sys.exit(1)
    selected_screen = screens[args.screen - 1]
    v4l2loopback_dev = get_v4l2loopback_dev()
    if v4l2loopback_dev is None:
        sys.exit(1)
    ffmpeg_cmd = ['ffmpeg', '-f', 'x11grab', '-framerate', '30', '-video_size',
                  '%dx%d' % (selected_screen.width, selected_screen.height),
                  '-i', ':0.0+%d,%d' % (selected_screen.x, selected_screen.y),
                  '-f', 'v4l2', '-vcodec', 'rawvideo', '-pix_fmt', 'rgb24',
                  v4l2loopback_dev]
    print('Executing ffmpeg cmd: ' + ' '.join(ffmpeg_cmd))
    global ffmpeg_proc
    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd)
    signal.signal(signal.SIGINT, send_signal)
    ffmpeg_proc.wait()


if __name__ == '__main__':
    main()
