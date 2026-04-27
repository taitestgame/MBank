import os
import io
import sys
import urllib.request
import onnxruntime as ort
from PIL import Image
import numpy as np

class OCRModel:
    def __init__(self, model_path: str = None):
        chars = [str(i) for i in range(10)] + [chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)]
        chars.sort()
        self.chars = chars
        
        if getattr(sys, 'frozen', False):
            current_dir = sys._MEIPASS
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.model_path = model_path or os.path.join(current_dir, 'model.onnx')
        self.session = None

    def load_model(self):
        if not os.path.exists(self.model_path):
            self._download_onnx_model()
        self.session = ort.InferenceSession(self.model_path)

    def _download_onnx_model(self):
        url = "https://github.com/thedtvn/mbbank-capcha-ocr/raw/refs/heads/master/mb_capcha_ocr/model.onnx"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(self.model_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)

    def predict(self, image_buffer: bytes) -> str:
        if self.session is None:
            self.load_model()
            
        img = Image.open(io.BytesIO(image_buffer)).convert('L')
        img = img.resize((160, 50))
        
        image_array = np.array(img, dtype=np.float32) / 255.0
        tensor = image_array.reshape((1, 1, 50, 160))
        
        input_name = self.session.get_inputs()[0].name
        results = self.session.run(None, {input_name: tensor})
        
        output_data = results[0]
        
        pred_labels = np.argmax(output_data, axis=2)[0]
        
        pred_text = ""
        for label in pred_labels:
            if 0 <= label < len(self.chars):
                pred_text += self.chars[label]
                
        return pred_text

def recognize_tesseract(image_buffer: bytes) -> str:
    try:
        import pytesseract
        img = Image.open(io.BytesIO(image_buffer))
        text = pytesseract.image_to_string(img, config='--psm 12 --oem 1 -l eng')
        return text.strip()
    except Exception as e:
        return ""
