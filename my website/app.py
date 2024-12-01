from flask import Flask, request, jsonify, render_template
import joblib
from cryptography.fernet import Fernet
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Load the model and vectorizer
model = joblib.load('sensitivity_model.pkl')
vectorizer = joblib.load("tfidf_vectorizer.pkl")

# Encryption setup
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Function to predict sensitivity and encrypt if sensitive
def predict_and_encrypt(text):
    # Preprocess the text input
    text_tfidf = vectorizer.transform([text])
    
    # Predict sensitivity
    prediction = model.predict(text_tfidf)[0]
    
    if prediction == 1:
        encrypted_text = cipher_suite.encrypt(text.encode()).decode("utf-8")  # Convert to string for JSON
        with open(r"C:\Users\DELL\Desktop\secret\encrypted_text.txt", "a") as file:
            file.write(encrypted_text)

        return "Sensitive", encrypted_text
    else:
        return "Non-Sensitive", None

@app.route('/predict', methods=['POST'])
def predict():
    # Extract the message entered by the user
    message = request.json.get("text")
    if not message:
        return jsonify({"error": "No text provided"}), 400
    
    result, encrypted_text = predict_and_encrypt(message)
    
    # Return the result as JSON
    return jsonify({"result": result, "encrypted_text": encrypted_text})


from cryptography.fernet import Fernet

# Load the encryption key from the file
with open("encryption_key.key", "rb") as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# Function to decrypt an encrypted message
def decrypt_text(encrypted_text):
    try:
        # Decode from string to bytes and decrypt
        decrypted_text = cipher_suite.decrypt(encrypted_text.encode()).decode()
        return decrypted_text
    except Exception as e:
        return f"Decryption failed: {str(e)}"
    
@app.route('/decrypt', methods=['POST'])
def decrypt():
    encrypted_text = request.form['encrypted_text']
    decrypted_text = decrypt_text(encrypted_text)  # Call your custom decryption function
    return render_template('index.html', decrypted_text=decrypted_text)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
