import tensorflow as tf
import tensorflow.keras.backend as K

def triplet_loss(y_true, y_pred, margin=0.3):
    anchor = y_pred[:, 0:128]
    positive = y_pred[:, 128:256]
    negative = y_pred[:, 256:384]
    pos_dist = K.sum(K.square(anchor - positive), axis=1)
    neg_dist = K.sum(K.square(anchor - negative), axis=1)
    loss = K.maximum(0.0, margin + pos_dist - neg_dist)
    return K.mean(loss)

def l2_normalize(x, axis=1):
    return K.l2_normalize(x, axis=1)

custom_objects = {
    'triplet_loss': triplet_loss,
    'l2_normalize': l2_normalize
}

model_path = './deep_rank_model_optimized_savedmodel'  # Đường dẫn thực tế
model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)

print("model.input:", model.input)