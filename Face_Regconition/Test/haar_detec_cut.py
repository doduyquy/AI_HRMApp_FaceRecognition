import cv2 as cv
import os
import time

def detectAndDisplay(frame, face_cascade, known_faces, last_saved_time):
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.equalizeHist(frame_gray)
    
    # faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.05, minNeighbors=21)
    faces = face_cascade.detectMultiScale(
                    frame_gray, 
                    scaleFactor=1.03,
	                minNeighbors=11, 
                    # minSize=(45, 45)
                    )
    current_time = time.time()
    for (x, y, w, h) in faces:
        face_roi = frame_gray[y:y+h, x:x+w]
        if not known_faces or not any(cv.norm(cv.resize(face_roi, (known_face.shape[1], known_face.shape[0])), known_face) < 1000 for known_face in known_faces):
            if not known_faces or current_time - last_saved_time >= 5:
                known_faces.append(face_roi)
                face_image = frame[y:y+h, x:x+w]
                face_filename = f"./tmp/face_{len(known_faces)}.jpg"
                cv.imwrite(face_filename, face_image)
                print(f"Saved {face_filename}")
                last_saved_time = current_time
        
        cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
    
    cv.imshow('Live Face Detection', frame)
    return last_saved_time

if not os.path.exists('./tmp'):
    os.makedirs('./tmp')

face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
if not face_cascade.load('./haarcascade_frontalface_default.xml'):
    print('--(!)Error loading face cascade')
    exit(0)

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print('--(!)Error opening video capture')
    exit(0)

known_faces = []
last_saved_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print('--(!)No captured frame -- Break!')
        break
    
    last_saved_time = detectAndDisplay(frame, face_cascade, known_faces, last_saved_time)
    
    if cv.waitKey(1) == 27:
        break

cap.release()
cv.destroyAllWindows()
