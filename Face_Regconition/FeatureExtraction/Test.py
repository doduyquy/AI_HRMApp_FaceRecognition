import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.models import load_model
from mtcnn import MTCNN
import matplotlib.pyplot as plt

# Định nghĩa hàm triplet_loss
def triplet_loss(y_true, y_pred, margin=0.3):
    anchor = y_pred[:, 0:128]
    positive = y_pred[:, 128:256]
    negative = y_pred[:, 256:384]
    pos_dist = K.sum(K.square(anchor - positive), axis=1)
    neg_dist = K.sum(K.square(anchor - negative), axis=1)
    loss = K.maximum(0.0, margin + pos_dist - neg_dist)
    return K.mean(loss)

# Định nghĩa hàm l2_normalize (dùng trong Lambda layer)
def l2_normalize(x, axis=1):
    return K.l2_normalize(x, axis=axis)

# Hàm tiền xử lý ảnh cho mô hình
def preprocess_image_for_model(image, target_size=(128, 128)):
    img = cv2.resize(image, target_size)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# Hàm trích xuất khuôn mặt từ ảnh
def extract_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detector = MTCNN()
    faces = detector.detect_faces(img_rgb)
    if len(faces) > 0:
        x, y, w, h = faces[0]['box']
        face = img_rgb[y:y+h, x:x+w]
        return face
    else:
        raise ValueError(f"Không tìm thấy khuôn mặt trong ảnh: {image_path}")

# Hàm vẽ khung và ghi chú trên ảnh
def draw_result(image_path, is_match, name="Do Duy Quy"):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detector = MTCNN()
    faces = detector.detect_faces(img_rgb)
    if len(faces) > 0:
        x, y, w, h = faces[0]['box']
        color = (0, 255, 0) if is_match else (255, 0, 0)
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
        label = name if is_match else "Failed"
        cv2.putText(img, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Load mô hình với custom objects
model_path = 'deep_rank_model.h5'
custom_objects = {
    'triplet_loss': triplet_loss,
    'l2_normalize': l2_normalize  # Thêm l2_normalize vào custom objects
}
model = load_model(model_path, custom_objects=custom_objects)

# Tạo mô hình con để lấy anchor_output
anchor_input = model.input[0]
anchor_output = model.output[:, 0:128]
anchor_model = tf.keras.Model(inputs=anchor_input, outputs=anchor_output)

# Đường dẫn đến các ảnh
original_image_path = 'doduyquy.jpg'
compare_image_paths = ['01.jpg', '05.jpg']

# Trích xuất khuôn mặt từ ảnh gốc
original_face = extract_face(original_image_path)
original_face_processed = preprocess_image_for_model(original_face)

# Trích xuất embedding từ ảnh gốc
original_embedding = anchor_model.predict(original_face_processed)

# Ngưỡng để xác định xem có phải cùng một người hay không
THRESHOLD = 0.5

# So sánh với từng ảnh
results = []
for compare_path in compare_image_paths:
    compare_face = extract_face(compare_path)
    compare_face_processed = preprocess_image_for_model(compare_face)
    compare_embedding = anchor_model.predict(compare_face_processed)
    distance = np.sqrt(np.sum(np.square(original_embedding - compare_embedding)))
    print(f"Khoảng cách giữa {original_image_path} và {compare_path}: {distance}")
    is_match = distance < THRESHOLD
    results.append((compare_path, is_match))

# Hiển thị kết quả
plt.figure(figsize=(15, 5))

# Ảnh gốc
plt.subplot(1, 3, 1)
original_img = cv2.imread(original_image_path)
original_img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
plt.imshow(original_img_rgb)
plt.title("Ảnh gốc (Do Duy Quy)")
plt.axis('off')

# Ảnh so sánh 1
plt.subplot(1, 3, 2)
result_img_1 = draw_result(results[0][0], results[0][1])
plt.imshow(result_img_1)
plt.title("So sánh với 01.jpg")
plt.axis('off')

# Ảnh so sánh 2
plt.subplot(1, 3, 3)
result_img_2 = draw_result(results[1][0], results[1][1])
plt.imshow(result_img_2)
plt.title("So sánh với 05.jpg")
plt.axis('off')

plt.show()