import pandas as pd
import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array, load_img

import random

# Path to the dataset
data_dir = "/home/nii/Downloads/LFW_Dataset/lfw-deepfunneled"
# Read file peopleDevTrain.csv
people_df = pd.read_csv("/home/nii/Downloads/LFW_Dataset/peopleDevTrain.csv")

# Create list of labels and paths to images
image_paths = []
labels = []

def get_image_paths_and_labels(data_dir, people_df):
    for _, row in people_df.iterrows():
        person_name = row['name']
        person_dir = os.path.join(data_dir, person_name)
        
        if os.path.isdir(person_dir):
            for image_name in os.listdir(person_dir):
                if image_name.endswith('.jpg'):
                    image_paths.append(os.path.join(person_dir, image_name))
                    labels.append(person_name)

# Tạo triplets (Anchor, Positive, Negative):
# - Anchor: Hình ảnh gốc
# - Positive: Hình ảnh cùng người với anchor
# - Negative: Hình ảnh khác người với anchor
def create_triplets(image_paths, labels, num_triplets=10000):
    triplets = []
    label_set = list(set(labels))
    
    for _ in range(num_triplets):
        # Chọn ngẫu nhiên một anchor
        anchor_idx = random.randint(0, len(image_paths) - 1)
        anchor_label = labels[anchor_idx]
        
        # Tìm tất cả các hình ảnh của cùng nhãn với anchor (positive)
        positive_candidates = [i for i, label in enumerate(labels) if label == anchor_label and i != anchor_idx]
        if len(positive_candidates) == 0:
            continue  # Bỏ qua nếu không có positive
        
        positive_idx = random.choice(positive_candidates)
        
        # Tìm một negative (khác nhãn)
        negative_label = random.choice([lbl for lbl in label_set if lbl != anchor_label])
        negative_candidates = [i for i, label in enumerate(labels) if label == negative_label]
        negative_idx = random.choice(negative_candidates)
        
        triplets.append((image_paths[anchor_idx], image_paths[positive_idx], image_paths[negative_idx]))
    
    return triplets

def preprocess_image(image_path, target_size=(221, 221)):
    # Đọc hình ảnh
    img = load_img(image_path, target_size=target_size)
    # Chuyển thành mảng numpy
    img_array = img_to_array(img)
    # Chuẩn hóa giá trị pixel về khoảng [0, 1]
    img_array = img_array / 255.0
    return img_array

# Tải và tiền xử lý triplets
def load_triplet_data(triplets):
    anchor_images = []
    positive_images = []
    negative_images = []
    
    for anchor_path, positive_path, negative_path in triplets:
        anchor_images.append(preprocess_image(anchor_path))
        positive_images.append(preprocess_image(positive_path))
        negative_images.append(preprocess_image(negative_path))
    
    return (np.array(anchor_images), np.array(positive_images), np.array(negative_images))




def main():
    # Load the dataset
    # Get image paths and labels
    get_image_paths_and_labels(data_dir, people_df)
    # Print the number of images and labels
    print(f"Number of images: {len(image_paths)}")
    print(f"Number of labels: {len(labels)}")

    # Create 10,000 triplets
    triplets = create_triplets(image_paths, labels, num_triplets=10000)
    print(f"Số triplets: {len(triplets)}")

    # Load and preprocess triplet data
    anchor_images, positive_images, negative_images = load_triplet_data(triplets)
    print(f"Anchor images shape: {anchor_images.shape}")
    print(f"Positive images shape: {positive_images.shape}")
    print(f"Negative images shape: {negative_images.shape}")


# Run main: 
if __name__ == "__main__":
    main()