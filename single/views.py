import math
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pandas as pd
import cv2
import easyocr
# from pytesseract import Output
# import pytesseract
import numpy as np
from math import dist


def indexpage(request):
	return render(request, 'single/index.html')


def upload(request):
    if request.method == 'POST' and request.FILES:
        upload = request.FILES['upload']
        fss = FileSystemStorage()
        file = fss.save(upload, upload)
        file_url = fss.url(file)
        image_cropped, cropped_img_height, cropped_img_width, img_height, img_width = image_cropper("." + file_url)
        digital_image = extract_image(image_cropped, cropped_img_width, cropped_img_height)
        return render(request=request, template_name='single/index.html', context={'file_url': file_url, 'img_width': img_width, 'img_height': img_height, 'image_cropped': image_cropped, 'cropped_img_width': cropped_img_width, 'cropped_img_height': cropped_img_height, 'digital_image':digital_image})
    return render(request, 'single/index.html')


def image_cropper(image_path):
    image = cv2.imread(image_path)
    img_width, img_height = math.ceil(image.shape[0]), math.ceil(image.shape[1])

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    for cnts in contours:
        peri = cv2.arcLength(cnts, True)
        approx = cv2.approxPolyDP(cnts, 0.02 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break
        else:
            print("No possible contours found")

    pts = screenCnt.reshape(4, 2)
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    (tl, tr, br, bl) = rect

    maxWidth = max(int(dist(br, bl)), int(dist(tr, tl)))
    maxHeight = max(int(dist(tr, br)), int(dist(tl, bl)))
    dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype = "float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    # warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    (thresh, warped) = cv2.threshold(cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY), 185, 255, cv2.THRESH_BINARY)
    cropped_img_height, cropped_img_width = math.ceil(warped.shape[0]/2), math.ceil(warped.shape[1]/2)

    cv2.imwrite('./media/scanned_image.jpg', warped)
    return './media/scanned_image.jpg', cropped_img_height, cropped_img_width, img_height, img_width


def extract_image(image_path, img_width, img_height):
    image = cv2.imread(image_path)
    inputCopy = image.copy()
    
    reader = easyocr.Reader(['en'])

    # CREATING NEW CANVAS
    white_img = np.zeros([inputCopy.shape[0], inputCopy.shape[1], 3], dtype=np.uint8)
    white_img.fill(255)
    
    reader = easyocr.Reader(['en'])
    detection_result = reader.detect(image, width_ths=0.7, mag_ratio=1.5)
    text_coordinates = detection_result[0][0]
    data = reader.recognize(image, horizontal_list=text_coordinates, free_list=[])

    for dd in data:
        string_data = dd[1]
        x1 = dd[0][0][0]
        y1 = dd[0][0][1]
        x2 = dd[0][2][0]
        y2 = dd[0][2][1]
        # cropped_img = cv2.rectangle(white_img, ((x1), (y1)), ((x2), (y2)), (0, 255, 0), 2)
        cropped_img = cv2.putText(white_img, string_data, (x1+40, y2), cv2.FONT_HERSHEY_DUPLEX, abs(y2-y1)/70, (0, 0, 0), 2)
    cv2.imwrite('./media/digital_image.jpg', cropped_img)
    return './media/digital_image.jpg'