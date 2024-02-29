from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import requests

app = Flask(__name__)
CORS(app)

TOKEN = "7094792264:AAEH-QrZhteAOaFoHoCZEk54iyzhud1Tck4"  # Replace with your Telegram bot token
TELEGRAM_CHAT_ID = "5949257717"  # Replace with your Telegram chat ID
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

MODEL = tf.keras.models.load_model("D:\\code of hackathon\\codes\\2")

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

# Define solutions for each disease
DISEASE_SOLUTIONS = {
    "Early Blight": "Apply fungicide X and increase watering.",
    "Late Blight": "Isolate infected plants and use fungicide Y.",
    "Healthy": "No disease detected. Keep monitoring for any changes.",
}

def read_file_as_image(data) -> np.ndarray:
    image = Image.open(BytesIO(data))
    image = image.resize((256, 256))
    image = np.array(image)
    return image

def predict_disease(image_data):
    image = read_file_as_image(image_data)
    img_batch = np.expand_dims(image, 0)
    predictions = MODEL.predict(img_batch)

    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = float(np.max(predictions[0]))

    return predicted_class, confidence

def send_to_telegram(message, image_data):
    # Send the image to Telegram bot
    files = {'photo': ('image.jpg', image_data)}
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': message}
    requests.post(TELEGRAM_API_URL, files=files, data=payload)

@app.route("/")
def index():
    return "Flask API is running."

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    image_data = image_file.read()

    # Perform prediction on the captured image
    predicted_class, confidence = predict_disease(image_data)

    # Get the solution for the predicted disease
    disease_solution = DISEASE_SOLUTIONS.get(predicted_class, "No solution available.")

    # Send the prediction results and solution to Telegram bot
    message = f"Prediction: {predicted_class}\nConfidence: {confidence}\nSolution: {disease_solution}"
    send_to_telegram(message, image_data)

    return jsonify({"message": "Image uploaded and processed successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
