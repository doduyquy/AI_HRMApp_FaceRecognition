from __future__ import print_function
import cv2 as cv

def detectAndDisplay(frame):
    # Chuyển đổi sang ảnh xám
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.equalizeHist(frame_gray)
    
    # Phát hiện khuôn mặt
    faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.05, minNeighbors=5)
    
    # Vẽ hình vuông màu xanh lá cây quanh khuôn mặt
    for (x, y, w, h) in faces:
        cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
    
    # Hiển thị khung hình
    cv.imshow('Live Face Detection', frame)

# Tải bộ phân loại khuôn mặt từ tệp XML
face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

# Kiểm tra xem tệp XML có tải thành công không
if not face_cascade.load('./haarcascade_frontalface_default.xml'):
    print('--(!)Error loading face cascade')
    exit(0)

# Mở camera (0 là camera mặc định)
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print('--(!)Error opening video capture')
    exit(0)

# Vòng lặp để xử lý video trực tiếp
while True:
    # Đọc từng khung hình từ camera
    ret, frame = cap.read()
    if not ret:  # Nếu không đọc được khung hình
        print('--(!)No captured frame -- Break!')
        break
    
    # Gọi hàm phát hiện và hiển thị
    detectAndDisplay(frame)
    
    # Thoát khi nhấn phím ESC (mã ASCII 27)
    if cv.waitKey(1) == 27:
        break

# Giải phóng tài nguyên
cap.release()
cv.destroyAllWindows()