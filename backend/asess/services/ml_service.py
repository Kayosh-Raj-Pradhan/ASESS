import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import io
import os
import json

# Classes as specified in the notebook
CLASSES = ['Cataract', 'Conjunctivitis', 'Eyelid', 'Normal', 'Uveitis', 'pterygium']
NUM_CLASSES = len(CLASSES)

class EyeDiseaseModel:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.resnet50(weights=None)
        self.model.fc = nn.Linear(self.model.fc.in_features, NUM_CLASSES)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model = self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_bytes: bytes) -> dict:
        """
        Returns a dict with:
          - prediction: str (class name)
          - confidence: float (0-100)
          - all_probabilities: dict {class_name: probability}
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_t = self.transform(img)
        batch_t = torch.unsqueeze(img_t, 0).to(self.device)

        with torch.no_grad():
            outputs = self.model(batch_t)
            probabilities = F.softmax(outputs, dim=1)[0]
            confidence, predicted_idx = torch.max(probabilities, 0)

            predicted_class = CLASSES[predicted_idx.item()]
            confidence_pct = round(confidence.item() * 100, 2)

            all_probs = {}
            for i, cls_name in enumerate(CLASSES):
                all_probs[cls_name] = round(probabilities[i].item() * 100, 2)

        return {
            "prediction": predicted_class,
            "confidence": confidence_pct,
            "all_probabilities": all_probs
        }

# Initialize the model globally
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "eye_disease_resnet50.pth")
eye_disease_model = None

try:
    if os.path.exists(MODEL_PATH):
        eye_disease_model = EyeDiseaseModel(MODEL_PATH)
        print(f"[ML] Eye disease model loaded successfully from {MODEL_PATH}")
    else:
        print(f"[ML] Model not found at {MODEL_PATH}")
except Exception as e:
    print(f"[ML] Error loading model: {e}")
