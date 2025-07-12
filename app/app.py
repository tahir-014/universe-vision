# app/app.py

import os
from flask import Flask, request, render_template, redirect, url_for
import tensorflow as tf
import numpy as np
from PIL import Image

# --- Flask setup ---
app = Flask(__name__)

# --- Load TFLite model ---
try:
    model_path = os.path.join('model', 'universe_vision.tflite')
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print("✅ TFLite model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading TFLite model: {e}")
    interpreter = None

# --- Labels (replace with your actual labels) ---
class_names = ['Class A', 'Class B', 'Class C']  # Add real class names here

# --- Prediction Function ---
def predict_image(img_array):
    img_array = img_array.astype(np.float32)
    img_array = img_array.reshape(input_details[0]['shape'])  # [1, height, width, 3]

    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    top_3_indices = np.argsort(output[0])[::-1][:3]
    predictions = [(class_names[i], float(output[0][i])) for i in top_3_indices]
    return predictions

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        image = Image.open(file).convert("RGB")
        image = image.resize((224, 224))  # Match input size
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = predict_image(img_array)
        return render_template('result.html', predictions=predictions)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
