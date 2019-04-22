# Tool for capturing your Linux screen and turning it into v4l2 device

Usuful tool for sharing single screen by turning the screen into v4l2 device.
For example, though Slack doesn't support sharing single screen in multiple screen environment on Linux, by this tool, Slack becomes able to share the screen as a pseudo webcam input.


## Requirement

- Linux
- kernel module `v4l2loopback` ("v4l2loopback-dkms" package on Debian)
- Python >= 2.7
- Python library `python-xlib` or `python3-xlib` (same name packages on Debian)
- ffmpeg with `v4l2` output and `x11grab` input
- `/dev/video*` rw permission
- `modprobe` permission for `--reload_v4l2loopback` option

## Command

### Show help

```
$ ./set_v4l2loopback_screen.py -h
usage: set_v4l2loopback_screen.py [-h] -s SCREEN [-r]

optional arguments:
  -h, --help            show this help message and exit
  -s SCREEN, --screen SCREEN
                        Set screen number to loopback to v4l2 device
  -r, --reload_v4l2loopback
                        Set if v4l2loopback module reloading is needed (root
                        permission is required)
```

### Example

Turn screen 1 into v4l2 device

```
$ sudo ./set_v4l2loopback_screen.py --screen 1 --reload_v4l2loopback
```

Then, you can choose pseudo v4l2 device on your applications.
