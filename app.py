from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
BASE_AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'base')
RECORDINGS_FOLDER = os.path.join(UPLOAD_FOLDER, 'recordings')
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, 'output')

@app.route('/merge', methods=['POST'])
def merge_audio():
    owner_id = request.form.get('owner_id')
    base_file = request.files.get('base_audio')
    name_file = request.files.get('name_audio')
    city_file = request.files.get('city_audio')

    if not all([owner_id, base_file, name_file, city_file]):
        return jsonify({'error': 'Missing parameters'}), 400

    base_path = os.path.join(BASE_AUDIO_FOLDER, secure_filename(base_file.filename))
    name_path = os.path.join(RECORDINGS_FOLDER, f'{owner_id}_name.mp3')
    city_path = os.path.join(RECORDINGS_FOLDER, f'{owner_id}_city.mp3')
    output_path = os.path.join(OUTPUT_FOLDER, f'{owner_id}_merged.mp3')

    base_file.save(base_path)
    name_file.save(name_path)
    city_file.save(city_path)

    try:
        cmd = f"ffmpeg -y -i {base_path} -i {name_path} -i {city_path} -filter_complex '[0:0][1:0][2:0]concat=n=3:v=0:a=1[out]' -map '[out]' {output_path}"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'status': 'success', 'output_file': output_path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
