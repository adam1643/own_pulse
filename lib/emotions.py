from keras.preprocessing.image import img_to_array
import cv2
from keras.models import load_model
import numpy as np


class Emotions(object):

    def __init__(self):
        # model paths
        self.emotion_model_path = 'lib/models/model_CNN.30-0.66.hdf5'

        # without compile=False code won't compile - Tensorflow
        self.emotion_model = load_model(self.emotion_model_path, compile=False)

        # labels of  emotion in polish language because of target user
        self.emotions_labels = ['Złość', 'Zniesmaczenie', 'Strach', 'Radość', 'Smutek', 'Zaskoczenie', 'Obojętność']
        self.last_predictions = np.array([0] * 7)
        self.last_max = None
        self.predictions_array = []
        self.predictions_mean = []
        self.emotions_measured = False

    def predict(self, frame, faces):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # When face is detected
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face = gray[y:y + h, x:x + w]
                # resize the image to be passed to the neural network
                resized_face = cv2.resize(face, (48, 48))
                resized_face = resized_face.astype("float32") / 255.0
                resized_face = img_to_array(resized_face)
                resized_face = np.expand_dims(resized_face, axis=0)

                predictions = self.emotion_model.predict(resized_face)[0]
                self.last_predictions = predictions
                # the dominant emotion is the one with the highest probability
                label = self.emotions_labels[predictions.argmax()]
                self.last_max = label

            if len(self.predictions_array) < 15:
                self.predictions_array.append(self.last_predictions)
            else:
                self.predictions_array.pop(0)
                self.predictions_array.append(self.last_predictions)

            a = np.array(self.predictions_array)
            self.predictions_mean = a.mean(axis=0)
            self.emotions_measured = True
            return self.predictions_mean

        return None

    def get_last_prediction(self):
        return self.predictions_mean

    def get_last_prediction_str(self):
        str1 = ""

        for index, (emotion, prob) in enumerate(zip(self.emotions_labels, self.predictions_mean)):
            # construct the label text
            str1 = str1 + "{}: {:0.2f}%".format(emotion, prob * 100) + "\n"

        return str1

    def get_best_emotion(self):
        if len(self.predictions_mean) is 0:
            return "---"
        return self.emotions_labels[np.array(self.predictions_mean).argmax()]
