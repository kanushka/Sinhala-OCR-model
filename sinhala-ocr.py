# @author: BLK Gayan
# @purpose: Read Sinhala characters in a image/photo

# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import numpy as np

def convert_to_sinhala_text(filepath, scale=80):
	# load the example image and convert it to grayscale
	image = cv2.imread(filepath)

	#resize image
	scale_percent = scale # percent of original size
	width = int(image.shape[1] * scale_percent / 100)
	height = int(image.shape[0] * scale_percent / 100)
	dim = (width, height)
	resized_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

	# grayscale image
	gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

	# check to see if we should apply thresholding to preprocess the image
	gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]		

	# make a check to see if median blurring should be done to remove noise
	gray = cv2.medianBlur(gray, 3)

	# write the grayscale image to disk as a temporary file so we can apply OCR to it
	filename = "{}.png".format(os.getpid())
	cv2.imwrite(filename, gray)

	# load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file
	text = pytesseract.image_to_string(Image.open(filename), lang='sin')
	os.remove(filename)

	return text