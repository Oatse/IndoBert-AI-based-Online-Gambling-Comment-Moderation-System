#!/usr/bin/env python3
"""
Flask API Service untuk Spam/Judol Detection menggunakan IndoBERT
"""

from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import warnings
import os
warnings.filterwarnings("ignore")

app = Flask(__name__)

class SpamDetectorAPI:
    def __init__(self, model_path="./src/models"):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_model()
    
    def load_model(self):
        """Load model dan tokenizer IndoBERT"""
        try:
            print(f"Loading model from {self.model_path}...")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

            # Load model with proper device handling
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path,
                torch_dtype=torch.float32,  # Ensure float32 to avoid meta tensor issues
                device_map=None,  # Don't use device_map to avoid meta tensors
                low_cpu_mem_usage=False  # Disable low memory usage to avoid meta tensors
            )

            # Move model to device properly
            self.model = self.model.to(self.device)

            self.model.eval()

            print(f"Model loaded successfully on {self.device}")

        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise e
    
    def predict(self, text):
        """Prediksi spam/judol"""
        try:
            if not text or text.strip() == "":
                return {
                    "is_spam": False,
                    "confidence": 0.0,
                    "label": "normal",
                    "error": "Empty text"
                }

            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Prediksi
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Get prediction results
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = torch.max(predictions).item()

            # Debug: Print all class probabilities
            print(f"Debug - All class probabilities: {predictions[0].tolist()}")
            print(f"Debug - Predicted class: {predicted_class}, Confidence: {confidence}")

            # Model adalah binary classifier (2 kelas)
            # 0 = normal, 1 = spam/judol
            is_spam = predicted_class == 1
            label = "spam" if is_spam else "normal"

            # Confidence adalah probabilitas maksimum dari prediksi
            final_confidence = confidence

            return {
                "is_spam": is_spam,
                "confidence": float(final_confidence),
                "label": label,
                "predicted_class": int(predicted_class)
            }

        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return {
                "is_spam": False,
                "confidence": 0.0,
                "label": "error",
                "error": str(e)
            }

# Inisialisasi detector
detector = SpamDetectorAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "model_loaded": detector.model is not None})

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint untuk prediksi spam/judol"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        result = detector.predict(text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """Endpoint untuk prediksi batch multiple texts"""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({"error": "No texts provided"}), 400
        
        texts = data['texts']
        if not isinstance(texts, list):
            return jsonify({"error": "texts must be a list"}), 400
        
        results = []
        for text in texts:
            result = detector.predict(text)
            results.append(result)
        
        return jsonify({"results": results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
