from PIL import Image
import cv2
import pytesseract
import numpy as np

cv2.startWindowThread()

words = {}

#if args["p"] == "blur":
#    b = True
#else:
#    b = False

def rotationCorrect(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE)

    filename = "progress.png"
    cv2.imwrite(filename, rotated)
    return prepareText(filename)


def prepareText(filename):
    image = cv2.imread(filename)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)[1]
    # thresh = cv2.medianBlur(thresh, 3)
    cv2.imwrite(filename, thresh)
    return printText(filename)


def printText(filename):
    return pytesseract.image_to_string(Image.open(filename))
