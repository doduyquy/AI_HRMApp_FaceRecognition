import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import imutils
import os

# Sử dụng đường dẫn tuyệt đối để tránh lỗi:
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Đường dẫn hiện tại: {current_dir}")

### Định nghĩa path cho các file đầu vào:
# Haar Cascade 
CASCADE_PATH = os.path.abspath(os.path.join(current_dir, "../models/haarcascade_frontalface_default.xml"))
print("Đường đẫn haarcascade: ", CASCADE_PATH)

# Model.pb path
PB_PATH = os.path.abspath(os.path.join(current_dir, "../models/20180402-114759.pb"))
print(f"Đường dẫn mô hình: {PB_PATH}")

# Data path
DATA_DIR_PATH = os.path.abspath(os.path.join(current_dir, "../../Data"))
# DATA_DIR_PATH = "/home/nii/Documents/FaceRecognition/Data"
print(f"Đường dẫn dữ liệu: {DATA_DIR_PATH}")

EMBEDDING_PATH = os.path.abspath(os.path.join(current_dir, "../models/embeddings.npy"))

# Định nghĩa các thông số cho nhận diện 
THRESHOLD = 0.8
SCALEFACTOR = 1.03
MINNEIGHBORS = 11



# Hàm tiền xử lý ảnh cho FaceNet
def preprocess_image_for_model(image, target_size=(160, 160)):
    img = cv2.resize(image, target_size)
    img = img / 255.0
    img = img - 0.5
    img = img * 2.0
    img = np.expand_dims(img, axis=0)
    return img

# Hàm trích xuất khuôn mặt từ ảnh sử dụng Haar Cascade
def extract_face(image_path, cascade_path=CASCADE_PATH):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    
    detector = cv2.CascadeClassifier(cascade_path)
    img = imutils.resize(img, width=900)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = detector.detectMultiScale(gray, scaleFactor=SCALEFACTOR,
                                      minNeighbors=MINNEIGHBORS, 
                                    #   minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        face = img[y:y+h, x:x+w]
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        return face_rgb
    else:
        raise ValueError(f"Không tìm thấy khuôn mặt trong ảnh: {image_path}")

# Hàm vẽ khung và ghi chú trên ảnh
# def draw_result(image_path, is_match, name="Random", cascade_path=CASCADE_PATH):
#     img = cv2.imread(image_path)
#     if img is None:
#         raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    
#     detector = cv2.CascadeClassifier(cascade_path)
#     img = imutils.resize(img, width=900)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
#     faces = detector.detectMultiScale(gray, scaleFactor=SCALEFACTOR,
#                                       minNeighbors=11, 
#                                     #   minSize=(30, 30),
#                                       flags=cv2.CASCADE_SCALE_IMAGE)
    
#     if len(faces) > 0:
#         x, y, w, h = faces[0]
#         color = (0, 255, 0) if is_match else (255, 0, 0)
#         cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
#         label = name if is_match else "Failed"
#         cv2.putText(img, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
#     return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Tải mô hình .pb
def load_pb_model(pb_path):
    with tf.io.gfile.GFile(pb_path, 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
    return graph

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

# Trích xuất và lưu đặc trưng cho tất cả người trong thư mục
embeddings_dict = {}

print("Trích xuất đặc trưng từ tất cả ảnh trong thư mục...")
for img_file in os.listdir(DATA_DIR_PATH):
    if img_file.endswith('.jpg') and '_' in img_file:
        name = img_file.split('_')[0]  # Lấy tên người từ tên file
        img_path = os.path.join(DATA_DIR_PATH, img_file)
        try:
            face = extract_face(img_path)
            face_processed = preprocess_image_for_model(face)
            embedding = get_embedding(face_processed)
            # Lưu đặc trưng theo tên người (trung bình nếu có nhiều ảnh)
            if name in embeddings_dict:
                embeddings_dict[name].append(embedding)
            else:
                embeddings_dict[name] = [embedding]
            print(f"Đã trích xuất đặc trưng cho {img_file}")
        except ValueError as e:
            print(e)

# Tính trung bình đặc trưng cho mỗi người
for name in embeddings_dict:
    embeddings_dict[name] = np.mean(embeddings_dict[name], axis=0)

# Lưu đặc trưng vào file
np.save(EMBEDDING_PATH, embeddings_dict)
# np.save('embeddings.npy', embeddings_dict)
print(f"Đã lưu đặc trưng vào {EMBEDDING_PATH}")

