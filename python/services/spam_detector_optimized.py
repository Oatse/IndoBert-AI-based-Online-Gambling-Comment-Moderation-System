#!/usr/bin/env python3
"""
Optimized Spam/Judol Detector Service menggunakan IndoBERT
Model dimuat sekali dan digunakan berulang kali untuk efisiensi
"""

import sys
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import warnings
import signal
import time
warnings.filterwarnings("ignore")

class OptimizedSpamDetector:
    def __init__(self, model_path="./python/models"):
        """
        Inisialisasi model IndoBERT untuk deteksi spam/judol
        """
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_model()
    
    def load_model(self):
        """Load model dan tokenizer IndoBERT"""
        try:
            print(f"Loading model from {self.model_path}...", file=sys.stderr)
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            
            # Load model
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            
            print(f"Model loaded successfully on {self.device}", file=sys.stderr)
            print("Ready for predictions. Send text input:", file=sys.stderr)
            
        except Exception as e:
            print(f"Error loading model: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    def predict(self, text):
        """
        Prediksi apakah teks adalah spam/judol atau tidak
        """
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
            
            # Mapping class ke label
            is_spam = predicted_class == 1
            label = "spam" if is_spam else "normal"
            
            return {
                "is_spam": is_spam,
                "confidence": float(confidence),
                "label": label,
                "predicted_class": int(predicted_class)
            }
            
        except Exception as e:
            return {
                "is_spam": False,
                "confidence": 0.0,
                "label": "error",
                "error": str(e)
            }

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down gracefully...", file=sys.stderr)
    sys.exit(0)

def main():
    """Main function untuk menjalankan service dalam mode interaktif"""
    signal.signal(signal.SIGINT, signal_handler)
    
    # Inisialisasi detector
    detector = OptimizedSpamDetector()
    
    # Mode interaktif - baca input dari stdin
    try:
        while True:
            line = sys.stdin.readline()
            if not line:  # EOF
                break
                
            text = line.strip()
            if text == "":
                continue
                
            if text.lower() == "quit" or text.lower() == "exit":
                break
            
            # Prediksi
            result = detector.predict(text)
            
            # Output hasil dalam format JSON
            print(json.dumps(result, ensure_ascii=False))
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    main()
