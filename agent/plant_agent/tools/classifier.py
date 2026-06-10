import os
import json
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
from PIL import Image
from pathlib import Path

CATEGORIES = [
    'Apple___healthy',                                        # 0
    'Apple___Apple_scab',                                     # 1
    'Apple___Black_rot',                                      # 2
    'Apple___Cedar_apple_rust',                               # 3
    'Blueberry___healthy',                                    # 4
    'Cherry_(including_sour)___healthy',                      # 5
    'Cherry_(including_sour)___Powdery_mildew',               # 6
    'Corn_(maize)___healthy',                                 # 7
    'Corn_(maize)___Common_rust_',                            # 8
    'Corn_(maize)___Northern_Leaf_Blight',                    # 9
    'Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot',     # 10
    'Grape___healthy',                                        # 11
    'Grape___Black_rot',                                      # 12
    'Grape___Esca_(Black_Measles)',                           # 13
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',             # 14
    'Orange___Haunglongbing_(Citrus_greening)',               # 15
    'Peach___healthy',                                        # 16
    'Peach___Bacterial_spot',                                 # 17
    'Pepper,_bell___healthy',                                 # 18
    'Pepper,_bell___Bacterial_spot',                          # 19
    'Potato___healthy',                                       # 20
    'Potato___Early_blight',                                  # 21
    'Potato___Late_blight',                                   # 22
    'Raspberry___healthy',                                    # 23
    'Soybean___healthy',                                      # 24
    'Squash___Powdery_mildew',                                # 25
    'Strawberry___healthy',                                   # 26
    'Strawberry___Leaf_scorch',                               # 27
    'Tomato___healthy',                                       # 28
    'Tomato___Bacterial_spot',                                # 29
    'Tomato___Early_blight',                                  # 30
    'Tomato___Late_blight',                                   # 31
    'Tomato___Leaf_Mold',                                     # 32
    'Tomato___Septoria_leaf_spot',                            # 33
    'Tomato___Spider_mites_Two-spotted_spider_mite',          # 34
    'Tomato___Target_Spot',                                   # 35
    'Tomato___Tomato_mosaic_virus',                           # 36
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',                 # 37
]

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" 

PREDICTION_FILE = DATA_DIR / "last_prediction.json"
 
_PREPROCESS = transforms.Compose([
    transforms.Resize((224, 224)), 
    transforms.ToTensor(),         
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

def _build_model(num_classes: int) -> nn.Module:
    model = models.mobilenet_v3_large(weights='IMAGENET1K_V2')
    in_features = 1280 
    model.classifier[-1] = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.BatchNorm1d(512),
        nn.ReLU(),
        nn.Dropout(p=0.5),
        
        nn.Linear(512, 128),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        
        nn.Linear(128, num_classes),
    )
    return model

def _load_model() -> nn.Module:
    """Build the model, load weights, set eval mode. Called once on import."""
    model_path = DATA_DIR / "model_mobilenet_finetuned.pth"
 
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model weights not found at {model_path}. "
            "Make sure model_mobilenet_finetuned.pth is inside the data/ directory."
        )
 
    model = _build_model(num_classes=len(CATEGORIES))
 
    state_dict = torch.load(
        str(model_path),
        map_location=torch.device("cpu"),
        weights_only=True,  
    )
    model.load_state_dict(state_dict)
    model.eval()
 
    print(f"[Model] Loaded from {model_path}")
    return model
 
 
_MODEL = _load_model()

CURRENT_IMAGE = None

LAST_PREDICTION = {
    "label": "",
    "confidence": 0.0,
    "top3": []
}

def save_prediction():
    PREDICTION_FILE.write_text(
        json.dumps(LAST_PREDICTION, indent=2)
    )


def load_prediction():

    if not PREDICTION_FILE.exists():
        return None

    try:
        return json.loads(
            PREDICTION_FILE.read_text()
        )

    except Exception:
        return None

def predict_disease() -> str:
    print("predict_disease called")
    global LAST_PREDICTION

    if not CURRENT_IMAGE:
        saved = load_prediction()
        
        print("Loaded prediction: ", saved)
        if saved:

            LAST_PREDICTION["label"] = saved["label"]
            LAST_PREDICTION["confidence"] = saved["confidence"]
            LAST_PREDICTION["top3"] = saved.get("top3", [])

            return (
                f"{saved['label']} "
                f"(confidence: {saved['confidence']:.2%})"
            )

        return "Error: No image supplied."

    if not os.path.exists(CURRENT_IMAGE):
        return f"Error: Image not found at {CURRENT_IMAGE}"
 
    try:
        img = Image.open(CURRENT_IMAGE).convert("RGB")
        batch_t = torch.unsqueeze(_PREPROCESS(img), 0)
 
        with torch.no_grad():
            outputs = _MODEL(batch_t)
            probabilities = torch.softmax(outputs, dim=1)
 
        confidence, index = torch.max(probabilities, dim=1)

        top3_probs, top3_idx = torch.topk(
            probabilities,
            3
        )

        result = CATEGORIES[index.item()]
        confidence_val = confidence.item()
 
        LAST_PREDICTION["top3"] = [
            {
                "label": CATEGORIES[idx.item()],
                "confidence": prob.item()
            }
            for prob, idx in zip(
                top3_probs[0],
                top3_idx[0]
            )
        ]
        
        LAST_PREDICTION["label"] = result
        LAST_PREDICTION["confidence"] = confidence_val

        save_prediction()

        print(f"[Prediction] {result}  |  confidence: {confidence_val:.4f}")
        return f"{result} (confidence: {confidence_val:.2%})"
 
    except Exception as e:
        return f"Error during prediction: {e}"