### TOI UU ### 
import cv2
import numpy as np
import tensorflow as tf
import imutils
import os
import time

# Lấy đường dẫn thư mục chứa Recognize_live.py
# Sử dụng đường dẫn tuyệt đối để tránh lỗi:
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Đường dẫn hiện tại: {current_dir}")

### Định nghĩa path cho các file đầu vào:
CASCADE_PATH = "../HaarCascade/haarcascade_frontalface_default.xml"
PB_PATH = os.path.abspath(os.path.join(current_dir, "../../Model/20180402-114759.pb"))
print(f"Đường dẫn mô hình: {PB_PATH}")

# Định nghĩa các thông số cho nhận diện 
THRESHOLD = 0.8 # Ngưỡng để xác định đúng người hay không: nhỏ hơn -> đúng, lớn hơn -> sai
FRAME_SKIP = 5  # Xử lý nhận diện mỗi 5 khung hình, để tránh lag
BLUE_EXPAND = 10  # Số pixel mở rộng khung xanh lam

# Hàm tiền xử lý ảnh cho 
def preprocess_image_for_model(image, target_size=(160, 160)):
    img = cv2.resize(image, target_size)
    img = img / 255.0
    img = img - 0.5
    img = img * 2.0
    img = np.expand_dims(img, axis=0)
    return img

# Hàm trích xuất khuôn mặt từ khung hình
def extract_face(image, cascade_path=CASCADE_PATH):
    img = imutils.resize(image, width=500)  # Giảm kích thước xuống 500 tránh quá tải
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier(cascade_path)
    
    faces = detector.detectMultiScale(gray, scaleFactor=1.03,
                                      minNeighbors=11, 
                                    #   minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        face = img[y:y+h, x:x+w]
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        return face_rgb, (x, y, w, h), img
    return None, None, img

# Tải mô hình .pb
def load_pb_model(pb_path):
    with tf.io.gfile.GFile(pb_path, 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
    return graph

# Trích xuất đặc trưng embedding của khuô mặt
def get_embedding_from_pb(graph, image_processed):
    with tf.compat.v1.Session(graph=graph) as sess:
        images_placeholder = graph.get_tensor_by_name('input:0')
        embeddings = graph.get_tensor_by_name('embeddings:0')
        phase_train_placeholder = graph.get_tensor_by_name('phase_train:0')
        feed_dict = {images_placeholder: image_processed, phase_train_placeholder: False}
        embedding = sess.run(embeddings, feed_dict=feed_dict)
    return embedding

# Tải mô hình
graph = load_pb_model(PB_PATH)

# Định nghĩa hàm lấy embedding
def get_embedding(image_processed):
    return get_embedding_from_pb(graph, image_processed)

# Hàm nhận diện qua camera
def recognize_from_camera(threshold=THRESHOLD, frame_skip=FRAME_SKIP, blue_expand=BLUE_EXPAND):
    # Tải đặc trưng đã lưu
    embeddings_dict = np.load('embeddings.npy', allow_pickle=True).item()
    
    # Mở camera 
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở camera")
        return
    
    print("Bắt đầu nhận diện qua camera. Nhấn 'q' để thoát.")
    
    frame_count = 0  # Đếm số khung hình để bỏ qua
    last_label = "Unknown"  # Nhãn cuối cùng để hiển thị khi bỏ qua khung
    last_color = (0, 0, 255)  # Màu cuối cùng (mặc định đỏ)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc khung hình từ camera")
            break
        
        frame_count += 1
        # Trích xuất khuôn mặt từ khung hình
        face, coords, processed_frame = extract_face(frame)
        
        # Luôn tô khung màu xanh lam khi phát hiện khuôn mặt
        if face is not None and coords is not None:
            x, y, w, h = coords
           
           # Mở rộng khung xanh lam để không khi đè khung xanh lá or đỏ
            blue_x = max(0, x - blue_expand)  # Đảm bảo không vượt biên trái
            blue_y = max(0, y - blue_expand)  # Đảm bảo không vượt biên trên
            blue_w = w + 2 * blue_expand  # Mở rộng chiều rộng
            blue_h = h + 2 * blue_expand  # Mở rộng chiều cao
            # Kiểm tra biên phải và dưới để không vượt kích thước ảnh
            blue_w = min(blue_w, processed_frame.shape[1] - blue_x)
            blue_h = min(blue_h, processed_frame.shape[0] - blue_y)
            
            # Vẽ khung xanh lam rộng hơn
            cv2.rectangle(processed_frame, (blue_x, blue_y), (blue_x + blue_w, blue_y + blue_h), (255, 0, 0), 2)  # Blue
            # cv2.rectangle(processed_frame, (x + 10, y + 10), (x+w+10, y+h+10), (255, 0, 0), 2)  # Blue, thickness=4
            
            # Chỉ nhận diện mỗi frame_skip khung hình
            if frame_count % frame_skip == 0:

                # Bắt đầu đo thời gian
                start_time = time.time()

                # Trích xuất đặc trưng và nhận diện
                face_processed = preprocess_image_for_model(face)
                face_embedding = get_embedding(face_processed)
                
                # So sánh với các đặc trưng đã lưu
                min_distance = float('inf')
                best_match_name = None
                
                for name, stored_embedding in embeddings_dict.items():
                    distance = np.sqrt(np.sum(np.square(face_embedding - stored_embedding)))
                    if distance < min_distance:
                        min_distance = distance
                        best_match_name = name
                
                # Xác định kết quả
                is_match = min_distance < threshold
                if is_match:
                    # Khung xanh lá với độ dày nhỏ hơn (2)
                    cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Green, thickness=2
                    last_label = best_match_name
                    last_color = (0, 255, 0)  # Green
                else:
                    # Khung đỏ với độ dày nhỏ hơn (2)
                    cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)  # Red, thickness=2
                    last_label = "Unknown"
                    last_color = (0, 0, 255)  # Red
            
                # Kết thúc đo thời gian
                end_time = time.time()
                processing_time = end_time - start_time
                # Hiển thị thời gian xử lý
                print(f"Thời gian xử lý: {processing_time:.5f} giây")

            # Đặt label lên khung đã nhận diện trước cho các khung bị bỏ qua
            cv2.putText(processed_frame, last_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, last_color, 2)
        
        # Hiển thị khung hình
        cv2.imshow('Face Recognition', processed_frame)
        
        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Giải phóng camera và đóng cửa sổ
    cap.release()
    cv2.destroyAllWindows()

# Chạy nhận diện từ camera
print("\nBắt đầu nhận diện từ camera...")
recognize_from_camera()


### ---- SOURCE ---- ###
# import cv2
# import numpy as np
# import tensorflow as tf
# import matplotlib.pyplot as plt
# import imutils
# import os

# # Lấy đường dẫn thư mục chứa Recognize.py
# current_dir = os.path.dirname(os.path.abspath(__file__))
# print(f"Đường dẫn hiện tại: {current_dir}")

# ### Define the path to all files:
# # Haar Cascade 
# CASCADE_PATH = "../HaarCascade/haarcascade_frontalface_default.xml"

# # Model.pb path
# PB_PATH = os.path.abspath(os.path.join(current_dir, "../../Model/20180402-114759.pb"))
# print(f"Đường dẫn mô hình: {PB_PATH}")

# # Data directory to extract features
# DATA_DIR_PATH = os.path.abspath(os.path.join(current_dir, "../../Data"))
# print(f"Đường dẫn dữ liệu: {DATA_DIR_PATH}")

# # Define some constants
# THRESHOLD = 0.8

# # Hàm tiền xử lý ảnh cho FaceNet
# def preprocess_image_for_model(image, target_size=(160, 160)):
#     img = cv2.resize(image, target_size)
#     img = img / 255.0
#     img = img - 0.5
#     img = img * 2.0
#     img = np.expand_dims(img, axis=0)
#     return img

# # Hàm trích xuất khuôn mặt từ ảnh hoặc khung hình
# def extract_face(image, cascade_path=CASCADE_PATH, is_file=False):
#     if is_file:
#         img = cv2.imread(image)
#     else:
#         img = image  # Đầu vào là khung hình từ camera
    
#     if img is None:
#         raise ValueError("Không thể xử lý ảnh/khung hình")
    
#     detector = cv2.CascadeClassifier(cascade_path)
#     img = imutils.resize(img, width=900)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
#     faces = detector.detectMultiScale(gray, scaleFactor=1.09,
#                                       minNeighbors=21, minSize=(30, 30),
#                                       flags=cv2.CASCADE_SCALE_IMAGE)
    
#     if len(faces) > 0:
#         x, y, w, h = faces[0]
#         face = img[y:y+h, x:x+w]
#         face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
#         return face_rgb, (x, y, w, h), img  # Trả về mặt, tọa độ và ảnh gốc
#     else:
#         return None, None, img  # Không tìm thấy khuôn mặt

# # Tải mô hình .pb
# def load_pb_model(pb_path):
#     with tf.io.gfile.GFile(pb_path, 'rb') as f:
#         graph_def = tf.compat.v1.GraphDef()
#         graph_def.ParseFromString(f.read())
#     with tf.Graph().as_default() as graph:
#         tf.import_graph_def(graph_def, name='')
#     return graph

# def get_embedding_from_pb(graph, image_processed):
#     with tf.compat.v1.Session(graph=graph) as sess:
#         images_placeholder = graph.get_tensor_by_name('input:0')
#         embeddings = graph.get_tensor_by_name('embeddings:0')
#         phase_train_placeholder = graph.get_tensor_by_name('phase_train:0')
#         feed_dict = {images_placeholder: image_processed, phase_train_placeholder: False}
#         embedding = sess.run(embeddings, feed_dict=feed_dict)
#     return embedding

# # Tải mô hình
# graph = load_pb_model(PB_PATH)

# # Định nghĩa hàm lấy embedding
# def get_embedding(image_processed):
#     return get_embedding_from_pb(graph, image_processed)

# # Hàm nhận diện qua camera
# def recognize_from_camera(threshold=THRESHOLD):
#     # Tải đặc trưng đã lưu
#     embeddings_dict = np.load('embeddings.npy', allow_pickle=True).item()
    
#     # Mở camera
#     cap = cv2.VideoCapture(0)  # 0 là camera mặc định, thay đổi nếu cần
#     if not cap.isOpened():
#         print("Không thể mở camera")
#         return
    
#     print("Bắt đầu nhận diện qua camera. Nhấn 'q' để thoát.")
    
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Không thể đọc khung hình từ camera")
#             break
        
#         # Trích xuất khuôn mặt từ khung hình
#         face, coords, processed_frame = extract_face(frame, is_file=False)
        
#         if face is not None and coords is not None:
#             x, y, w, h = coords
#             # Trích xuất đặc trưng
#             face_processed = preprocess_image_for_model(face)
#             face_embedding = get_embedding(face_processed)
            
#             # So sánh với các đặc trưng đã lưu
#             min_distance = float('inf')
#             best_match_name = None
            
#             for name, stored_embedding in embeddings_dict.items():
#                 distance = np.sqrt(np.sum(np.square(face_embedding - stored_embedding)))
#                 if distance < min_distance:
#                     min_distance = distance
#                     best_match_name = name
            
#             # Xác định kết quả
#             is_match = min_distance < threshold
#             label = best_match_name if is_match else "Failed"
#             color = (0, 255, 0) if is_match else (0, 0, 255)  # Xanh cho đúng, đỏ cho sai
            
#             # Vẽ khung và nhãn lên khung hình
#             cv2.rectangle(processed_frame, (x, y), (x+w, y+h), color, 2)
#             cv2.putText(processed_frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
#         # Hiển thị khung hình
#         cv2.imshow('Face Recognition', processed_frame)
        
#         # Nhấn 'q' để thoát
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
    
#     # Giải phóng camera và đóng cửa sổ
#     cap.release()
#     cv2.destroyAllWindows()

# # Chạy nhận diện từ camera
# print("\nBắt đầu nhận diện từ camera...")
# recognize_from_camera()