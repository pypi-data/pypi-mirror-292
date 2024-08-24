from picamera2 import Picamera2

IMG_DIMS = (1280, 720)

def main():
    picam = setup_camera_gray()
    while True:
        img = picam.capture_array()
        img_preproc = img[:IMG_DIMS[1], :IMG_DIMS[0]]


def setup_camera_gray():
    picam = Picamera2()
    config = picam.create_preview_configuration()
    config['main']['size'] = IMG_DIMS
    config['main']['format'] = "YUV420"
    picam.align_configuration(config)
    print(config)
    picam.configure(config)
    picam.start()

    return picam
