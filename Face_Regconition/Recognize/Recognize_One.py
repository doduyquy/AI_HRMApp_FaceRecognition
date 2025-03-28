import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import imutils
import os

# Hàm tiền xử lý ảnh cho FaceNet
def preprocess_image_for_model(image, target_size=(160, 160)):
    img = cv2.resize(image, target_size)
    img = img / 255.0
    img = img - 0.5
    img = img * 2.0
    img = np.expand_dims(img, axis=0)
    return img

# Hàm trích xuất khuôn mặt từ ảnh sử dụng Haar Cascade
def extract_face(image_path, cascade_path="./HaarCascade/haarcascade_frontalface_default.xml"):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    
    detector = cv2.CascadeClassifier(cascade_path)
    img = imutils.resize(img, width=900)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = detector.detectMultiScale(gray, scaleFactor=1.09,
                                      minNeighbors=21, minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        face = img[y:y+h, x:x+w]
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        return face_rgb
    else:
        raise ValueError(f"Không tìm thấy khuôn mặt trong ảnh: {image_path}")

# Hàm vẽ khung và ghi chú trên ảnh
def draw_result(image_path, is_match, name="Random", cascade_path="./HaarCascade/haarcascade_frontalface_default.xml"):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    
    detector = cv2.CascadeClassifier(cascade_path)
    img = imutils.resize(img, width=900)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = detector.detectMultiScale(gray, scaleFactor=1.09,
                                      minNeighbors=21, minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        color = (0, 255, 0) if is_match else (255, 0, 0)
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
        label = name if is_match else "Failed"
        cv2.putText(img, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

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
pb_path = '../Model/20180402-114759.pb'
graph = load_pb_model(pb_path)

# Định nghĩa hàm lấy embedding
def get_embedding(image_processed):
    return get_embedding_from_pb(graph, image_processed)

# Trích xuất và lưu đặc trưng của 5 ảnh Quy_01.jpg đến Quy_05.jpg
data_dir = '../Data'
image_files = [f'Quy_0{i}.jpg' for i in range(1, 6)]
embeddings_dict = {}

print("Trích xuất đặc trưng từ 5 ảnh...")
for img_file in image_files:
    img_path = os.path.join(data_dir, img_file)
    try:
        face = extract_face(img_path)
        face_processed = preprocess_image_for_model(face)
        embedding = get_embedding(face_processed)
        embeddings_dict[img_file] = embedding
        print(f"Đã trích xuất đặc trưng cho {img_file}")
    except ValueError as e:
        print(e)

# Lưu đặc trưng vào file (tùy chọn)
np.save('embeddings.npy', embeddings_dict)
print("Đã lưu đặc trưng vào embeddings.npy")

# Hàm test nhận diện ảnh anchor.jpg
def test(anchor_path='./anchor.jpg', threshold=0.8):
    # Tải đặc trưng đã lưu
    embeddings_dict = np.load('embeddings.npy', allow_pickle=True).item()
    
    # Trích xuất đặc trưng từ ảnh anchor
    try:
        anchor_face = extract_face(anchor_path)
        anchor_face_processed = preprocess_image_for_model(anchor_face)
        anchor_embedding = get_embedding(anchor_face_processed)
    except ValueError as e:
        print(e)
        return
    
    # So sánh với các đặc trưng đã lưu
    min_distance = float('inf')
    best_match = None
    
    for img_file, stored_embedding in embeddings_dict.items():
        distance = np.sqrt(np.sum(np.square(anchor_embedding - stored_embedding)))
        print(f"Khoảng cách giữa {anchor_path} và {img_file}: {distance}")
        if distance < min_distance:
            min_distance = distance
            best_match = img_file
    
    # Xác định kết quả
    is_match = min_distance < threshold
    name = "Quy" if is_match else "Failed"
    
    # Vẽ kết quả
    result_img = draw_result(anchor_path, is_match, name=name)
    plt.figure(figsize=(5, 5))
    plt.imshow(result_img)
    plt.title(f"Kết quả nhận diện: {name}")
    plt.axis('off')
    plt.show()

# Chạy hàm test
print("\nKiểm tra nhận diện ảnh anchor.jpg...")
test()