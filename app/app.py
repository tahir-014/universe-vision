from flask import Flask, render_template, request
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
import os

app = Flask(__name__)

# Load model once at startup
model_path = os.path.join("model", "universe_vision.h5")
model = load_model(model_path)

# CIFAR-10 Labels
labels = ['airplane', 'automobile', 'bird', 'cat', 'deer',
          'dog', 'frog', 'horse', 'ship', 'truck']

@app.route("/", methods=["GET", "POST"])
def index():
    top3 = None
    if request.method == "POST":
        image = request.files["image"]

        try:
            # Resize image to 32x32
            img = Image.open(image).resize((32, 32))
            img_array = np.expand_dims(np.array(img) / 255.0, axis=0)

            # Predict
            pred = model.predict(img_array)[0]
            top3_idx = pred.argsort()[-3:][::-1]  # Top 3 predictions
            top3 = [(labels[i], round(float(pred[i]) * 100, 2)) for i in top3_idx]

        except Exception as e:
            top3 = [("❌ Error processing image", 0)]

    return render_template("index.html", top3=top3)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
