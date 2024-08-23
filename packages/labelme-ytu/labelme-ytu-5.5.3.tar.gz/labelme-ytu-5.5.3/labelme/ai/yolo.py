import os
from os.path import exists
from urllib.parse import urlparse
import cv2

from labelme.widgets import ErrorDialog

import sys

#ultralytics gives error if stdout is None
if sys.stdout is None:
    f = open(os.devnull, 'w')
    sys.stdout = f

class Yolo:
    model_path = ""

    def __init__(self, model_path, track=False):
        self.model_path = model_path
        self.track = track
        try:
            import importlib
            ultralytics = importlib.import_module('ultralytics')
            YOLO = getattr(ultralytics, 'YOLO')
            self.model = YOLO(self.model_path)
        except (ImportError, AttributeError) as e:
            msgBox = ErrorDialog(f"Error loading YOLO model: {e}")
            msgBox.show()
            return None

    @staticmethod
    def getUniqueName(path):
        parent_folder = os.path.basename(os.path.dirname(path))
        file_name = os.path.basename(path)
        return f"{parent_folder}/{file_name}"

    @staticmethod
    def getFileName(path):
        return os.path.basename(path)

    def setModel(self, path):
        self.model_path = path

    def getResults(self, image_path):
        if not self.model_path.lower().endswith(".pt"):
            msgBox = ErrorDialog("Could not run the model.\nCheck model path in AI -> Object Detection Model.")
            msgBox.show()
            return None
        
        if not self.track:
            results = self.model(image_path)
        else:
            img = cv2.imread(image_path)
            results = self.model.track(img, persist=True)
        return results




    
