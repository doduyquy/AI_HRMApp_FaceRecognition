# import the necessary packages
import argparse
import imutils
import cv2
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, required=True,
	help="path to input image")
ap.add_argument("-c", "--cascade", type=str,
	default="haarcascade_frontalface_default.xml",
	help="path to haar cascade face detector")
args = vars(ap.parse_args())

# load the haar cascade face detector from
print("[INFO] loading face detector...")
detector = cv2.CascadeClassifier(args["cascade"])
# load the input image from disk, resize it, and convert it to
# grayscale
image = cv2.imread(args["image"])
# check if the image was successfully loaded
if image is None:
    print(f"[ERROR] could not read image from {args['image']}")
    exit()

image = imutils.resize(image, width=900)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# detect faces in the input image using the haar cascade face
# detector
print("[INFO] performing face detection...")
faces = detector.detectMultiScale(gray, scaleFactor=1.09,
	minNeighbors=21, minSize=(30, 30),   
	flags=cv2.CASCADE_SCALE_IMAGE)
print("[INFO] {} faces detected...".format(len(faces)))
# loop over the bounding boxes
for (x, y, w, h) in faces:
	# draw the face bounding box on the image
	cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
# show the output image

# Cắt và lưu khuôn mặt đã phát hiện trong ảnh input: 
# Cắt và lưu từng khuôn mặt
for i, (x, y, w, h) in enumerate(faces):
    # Cắt vùng khuôn mặt từ ảnh gốc
    face_roi = image[y:y+h, x:x+w]
    # Lưu khuôn mặt đã cắt
    cv2.imwrite(f"face_{i}.jpg", face_roi)
    
cv2.imshow("Face", face_roi)

     
# cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()