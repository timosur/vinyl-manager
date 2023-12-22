from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

from components.key_detection.main import analyze_audio_file
from components.tempo_detection.main import get_tempo

app = Flask(__name__)

@app.route('/analyze_audio', methods=['POST'])
def analyze_audio_route():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Secure the filename before saving it directly
        filename = secure_filename(file.filename)
        
        # Ensure files directory exists
        os.makedirs('files', exist_ok=True)

        # You can save the file to a directory (optional)
        file_path = os.path.join('files', filename)
        file.save(file_path)

        # Analyze tempo
        utempo = get_tempo(file_path)

        # Analyze key
        key_name, camelot_key, open_key_key = analyze_audio_file(file_path)

        # Create response
        response = {
            'detected_tempo': float(utempo),
            'detected_key': key_name,
            'camelot_key_notation': camelot_key,
            'open_key_notation': open_key_key
        }
        
        # Cleanup
        os.remove(file_path)

        return jsonify(response)

# Set a maximum size for the uploaded file
app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024 # For example, 16MB max size

if __name__ == '__main__':
    # listen on all IPs
    app.run(host='0.0.0.0', port=5000)
