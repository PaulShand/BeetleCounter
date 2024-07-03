from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from BeetleCounter import count_beetles
import os
import cv2

# Starts Flask app
app = Flask(__name__)

# Enforce Folders are made
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Prints out traffic
@app.before_request
def log_request_info():
    print(f"Request Headers: {request.headers}")

# Accepts POST from route /upload
@app.route('/upload', methods=['POST'])
def upload_file():
    # Checks a file is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']

    # Ensure the file not empty
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Save the original file
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    # tries to process image if anything goes bad tell it to grab the ERROR image
    try:
        # Process the image
        beetle_count, processed_image = count_beetles(file_path)

        # Save the processed image
        processed_filename = f"processed_{filename}"
        processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        cv2.imwrite(processed_file_path, processed_image)
    except Exception:
        processed_filename = f"ERROR.png"
        processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        beetle_count = 0

    # Return success response
    return jsonify({
        "message": "File uploaded and processed successfully",
        "processed_file_url": f"/processed/{processed_filename}",
        "beetle_count": beetle_count
    }), 200


# Receives the image at specific location
@app.route('/processed/<filename>', methods=['GET'])
def get_processed_file(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
