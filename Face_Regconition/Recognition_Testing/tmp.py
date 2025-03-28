import h5py

model_path = './facenet_keras.h5'
with h5py.File(model_path, 'r') as f:
    print(list(f.keys()))