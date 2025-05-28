@app.route('/merge', methods=['POST'])
def merge_audio():
    owner_id = request.form.get('owner_id')
    base_audio = request.files.get('base_audio')
    name_audio = request.files.get('name_audio')
    city_audio = request.files.get('city_audio')

    if not all([base_audio, name_audio, city_audio]):
        return jsonify({'error': 'Missing audio files'}), 400

    # Save all input audio temporarily
    base_path = os.path.join(UPLOAD_FOLDER, f'{owner_id}_base.mp3')
    name_path = os.path.join(UPLOAD_FOLDER, f'{owner_id}_name.mp3')
    city_path = os.path.join(UPLOAD_FOLDER, f'{owner_id}_city.mp3')
    merged_filename = f'merged_{owner_id}.mp3'
    merged_path = os.path.join(MERGED_FOLDER, merged_filename)

    base_audio.save(base_path)
    name_audio.save(name_path)
    city_audio.save(city_path)

    # Merge audio using ffmpeg
    command = [
        'ffmpeg', '-y',
        '-i', f'concat:{base_path}|{name_path}|{city_path}',
        '-acodec', 'copy', merged_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if not os.path.exists(merged_path):
        return jsonify({'error': 'Failed to merge audio'}), 500

    # Upload to Google Drive
    gdrive_url = upload_to_drive(merged_path, parent_folder_id='1WX54Z6xGPIymu4DFvPgTLX8_0zsWD3V3')

    # Log to Google Sheets
    try:
        append_row_to_active_sheet(name_audio.filename.rsplit('.', 1)[0], city_audio.filename.rsplit('.', 1)[0], gdrive_url)
    except Exception as e:
        print("Logging to sheet failed:", e)

    return jsonify({
        'message': 'Audio merged and uploaded successfully',
        'output_file': merged_filename,
        'gdrive_url': gdrive_url
    })
