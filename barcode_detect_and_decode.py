from os import listdir
from os.path import isfile, join
import argparse
import cv2   # pip install opencv-python
from pyzbar.pyzbar import decode

def preprocess(image):
	# load the image
	image = cv2.imread(args["image"])

	#resize image
	image = cv2.resize(image, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_CUBIC)

	#convert to grayscale
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	#calculate x & y gradient
	gradX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
	gradY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

	# subtract the y-gradient from the x-gradient
	gradient = cv2.subtract(gradX, gradY)
	gradient = cv2.convertScaleAbs(gradient)

	# blur the image
	blurred = cv2.blur(gradient, (3, 3))

	# threshold the image
	(_, thresh) = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)
	thresh = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	return thresh

# decode barcode
def barcode(image_read, is_preprocess):
	if is_preprocess:
		image_read = preprocess(image_read)

	barcodes = decode(image_read)

	for barcode in barcodes:
		barcode_data = barcode.data.decode("utf-8")
		barcode_type = barcode.type
		(x, y, w, h) = barcode.rect

		print("[INFO] code: {} || image: {} || format {} || Location: x {}, y {}, w {}, h {}".format(
			barcode_data, image_in_folder, barcode_type, x, y, w, h))

	if not len(barcodes):
		print("[NOT FOUND] on this page")

	print('-----------------------------------------------------------------------')
	del(image_read)


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False, help="path to the image file")
ap.add_argument("-d", "--dir", required=False, help="path to the images folder")
ap.add_argument("-pre", "--preprocess", required=False, help="pre process images")

args = vars(ap.parse_args())
image_dir = args["dir"]
image_file_name = args["image"]
is_preprocess = args["preprocess"]
if is_preprocess:
	print('this is not always working properly')

if not image_dir and not image_file_name:
	print("required path to the image file or images dir using --image or --dir")
if image_dir:
	images = [f for f in listdir(image_dir) if isfile(join(image_dir, f))]
	for image_in_folder in images:		
		image_read_in_folder = cv2.imread(image_dir+'/'+image_in_folder, 0)
		barcode(image_read_in_folder, is_preprocess)
else:
	image_read = cv2.imread(image_file_name, 0)
	barcode(image_read, is_preprocess)
