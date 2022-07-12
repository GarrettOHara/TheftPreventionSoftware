"""
Webcam.py takes & stores webcam images and allows access through filename
or pickled bytes

Anthony Norderhaug, CS-578-01, Group 10
"""
import cv2 # pip install opencv-python
import pickle
import traceback
from datetime import datetime

try_range = range(0, 3)
valid_cam_idxs = []

for i in try_range:
    cam = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    accessed, img = cam.read()  # FORMAT: bool, Image obj
    if accessed:
        valid_cam_idxs.append(i)

    cam.release()


def capture_all():
    images = []
    for cam_idx in valid_cam_idxs:
        cam = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
        accessed, img = cam.read()  # FORMAT: bool, Image obj

        if accessed:
            images.append(img)

    cam.release()

    return images

def capture():
    """
    accesses camera and takes picture. Saves in directory
    :return:            bytes, Image serialized or None, no camera access
    """
    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    accessed, img = cam.read()  # FORMAT: bool, Image obj
    file_name = datetime.now().strftime('%m_%d_%Y_%H_%M_%S.png')  # Timestamp

    if not accessed:
        return None  # camera can't be accessed
    else:
        cv2.imwrite(file_name, img)
        print("Photo successfully taken.")

    cam.release()

    return pickle.dumps(img)


def preview(img_input: any):
    """
    opens new window to preview image. specified by image bytes or pre-existing file name
    :param img_input:   bytes or str, relating to image
    :return:            True if preview successful, False otherwise
    """
    try:
        if isinstance(img_input, bytes):  # byte preview
            ret, buff = cv2.imencode('.png', pickle.loads(img_input))
            img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
        elif isinstance(img_input, str):  # file name preview
            img = cv2.imread(img_input)
        else:
            print("!INVALID INPUT DATA TYPE")
            return False

        cv2.imshow('preview', img)
        cv2.waitKey(0)  # displays preview, press any key to progress
        return True
    except Exception as err:
        print(traceback.format_exc())
        return False


if __name__ == '__main__':
    # NOTE: UNCOMMENT WHICH BASE CASES TO RUN
    # Only run 1 base case at a time. Multiple causes big lag. Might deal with webcam being open & closed for each
    # capture() call

    # TEST CASE 1: Capturing image
    capture()
    #print(valid_cam_idxs)
    #print(len(capture_all()))
    #
    # # TEST CASE 2: Capturing image and previewing with pickled bytes
    # pickle_bytes = capture()
    # preview(pickle_bytes)
    #
    # # TEST CASE 3: Previewing an image with file name
    # preview('09_19_2021_22:42:03.png')
