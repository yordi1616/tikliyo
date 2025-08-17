import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# A dictionary to act as our simple, in-memory database
# Note: Data will be lost on app restart/redeployment on Render's free tier
audio_files_db = {}
next_id = 1

# Configure the upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    # Sort files by views in descending order
    sorted_files = sorted(audio_files_db.items(), key=lambda item: item[1]['views'], reverse=True)
    return render_template('index.html', audio_files=sorted_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    global next_id
    if 'audio' not in request.files:
        return 'No audio file part'
    file = request.files['audio']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Add file to our simple database
        audio_files_db[str(next_id)] = {
            'filename': filename,
            'views': 0,
            'likes': 0
        }
        next_id += 1
        return redirect(url_for('index'))
    return 'Something went wrong'

@app.route('/play/<file_id>')
def play_audio(file_id):
    if file_id in audio_files_db:
        audio_files_db[file_id]['views'] += 1
        return redirect(url_for('static_audio_file', filename=audio_files_db[file_id]['filename']))
    return 'File not found', 404

@app.route('/like/<file_id>')
def like_audio(file_id):
    if file_id in audio_files_db:
        audio_files_db[file_id]['likes'] += 1
        return redirect(url_for('index'))
    return 'File not found', 404
    
# Serve audio files from the uploads directory
from flask import send_from_directory
@app.route('/uploads/<filename>')
def static_audio_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
