import os
from ndproject import config
from keras.models import load_model

IMAGE_LENGTH = 256
MODEL_PATH = config.NUDITY_DETECTION_MODEL_PATH

classifier = load_model(MODEL_PATH, compile=False)
classifier._make_predict_function()

from keras.preprocessing import image
import numpy as np
import cv2

labels = ['nsfw', 'sfw']

class NudityDetection():
    def __init__(self):
        pass

    def detect(self, img):
        resized = cv2.resize(img, (IMAGE_LENGTH, IMAGE_LENGTH), interpolation = cv2.INTER_AREA) 
        img_tensor = image.img_to_array(resized)
        img_tensor = np.expand_dims(img_tensor, axis=0)
        img_tensor /= 255. 
        pred_prob = classifier.predict(img_tensor)[0]
        idx = np.argmax(pred_prob)
        return labels[idx], pred_prob * 100

