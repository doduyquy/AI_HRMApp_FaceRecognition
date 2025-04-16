import argparse		# xử lí tham số dòng lệnh cmd-args
import imutils		# để thay đổi kích cỡ của image đầu vào để thuận tiện cho việc nhận dạng
import cv2			# xử lí ảnh
import time			# tính thời gian thực thi của thuật toán

###  construct the argument parser and parse the arguments
# tạo đối tượng ArgumentParser() để phân tích cmd-args
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, required=True,
	help="path to input image")

# Đặt path to file phát hiện khuôn mặt 
ap.add_argument("-c", "--cascade", type=str,
	default="haarcascade_frontalface_default.xml",
	help="path to haar cascade face detector")
# Chuyển các tham số về -> dict, để dễ truy cập
args = vars(ap.parse_args())

# Tạo đối tượng để phát hiện từ mô hình đã được truyền ở trên
print("[INFO] loading face detector...")
detector = cv2.CascadeClassifier(args["cascade"])

image = cv2.imread(args["image"])
if image is None:
    print(f"[ERROR] could not read image from {args['image']}")
    exit()

# Đặt kích thước ảnh cố định để thuận tiện cho việc xử lí
image = imutils.resize(image, width=900)
# Chuyển ảnh màu (ảnh gốc) sang ảnh xám (grayscale) để phát hiện khuôn mặt
# vì thuật toán Haar làm tốt hơn trên ảnh xám (đơn kênh) này
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

start = time.time()		# Đặt thời gian bắt đầu quá trình phát hiện
print("[INFO] performing face detection...")

""" gray			:	Ảnh xám đầu vào đã được chuyển đổi trước đó
	scaleFactor 	:	- Tỉ lệ thu nhỏ slide window đối với mỗi lần trượt qua toàn bộ ảnh
						VD: 1.09 -> giảm 9% mỗi lần
                    	- Tham số này thích hợp trong việc xác định nhiều khuôn mặt | khuôn mặt xa, gần
                    	tuy nhiên khi đã set size ảnh cố định và thực tế thì khi chấm công, 
                        công nhân đưa khuôn mặt vào gần vào camera nên không quá khó trong việc
                        điều chỉnh tham số này
                        
	minNeighbors	:	- trong một cửa sổ, nếu xác định là khuôn mặt thì các window gần đó
						cũng phải xác định đó là khuôn mặt (số lượng tối thiểu)
                        - Nếu tham số quá thấp: có thể xác định nhầm vật thể là khuôn mặt
                        - Nếu tham số quá cao: có thể bỏ qua khuôn mặt đúng
                        
	minSize			: 	- Kích thước tối thiểu cho một khuôn mặt, nếu nhỏ hơn thì bỏ qua
						- Do vậy việc set kích thước ảnh ban đầu và tỉ lệ scaleFactor kêt hợp với minSize 
                        rất quan trọng trong việc xác định đúng
"""
faces = detector.detectMultiScale(gray, scaleFactor=1.09,
	minNeighbors=21, minSize=(30, 30),   
	flags=cv2.CASCADE_SCALE_IMAGE)		# window được thu nhỏ trong quá trình quét

print("[INFO] {} faces detected...".format(len(faces)))

# Đặt thời gian kết thúc quá trình phát hiện và tính thời gian
end = time.time()
print("Execution time: ", str(end - start))

# Vẽ khung đối với khuôn mặt được phát hiện:
for (x, y, w, h) in faces:
    #	x, y	:	tọa độ góc trái trên của khuôn mặt
    # 	w, h	: 	weight và height của khuôn mặt
	cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Cắt và lưu khuôn mặt đã phát hiện trong ảnh input: 
# Cắt và lưu từng khuôn mặt
for i, (x, y, w, h) in enumerate(faces):
    # Cắt vùng khuôn mặt từ ảnh gốc
    face_roi = image[y:y+h, x:x+w]
    # Lưu khuôn mặt đã cắt
    cv2.imwrite(f"face_{i}.jpg", face_roi)
    # Hiển thị khuôn mặt đã cắt:
    cv2.imshow(f"Face_{i}", face_roi)
    
# cv2.imshow("Face", face_roi)

     
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()