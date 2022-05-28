import os
import io
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template,jsonify,json
from werkzeug.utils import secure_filename
from utils.face_analysis import get_analysis


UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


@app.route('/')
def start_page():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        statement='No file part'
        return render_template('index.html',statement=statement)
    file = request.files['file']
    if file.filename == '':
        statement='No image selected for uploading'
        return render_template('index.html', statement=statement)
    if file and allowed_file(file.filename):
        for filename in os.listdir('static/uploads/'):
            os.remove('static/uploads/' + filename)
        for filename in os.listdir('static/result/'):
            os.remove('static/result/' + filename)

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        response,statement = get_analysis(filename)
        return render_template('index.html',filename=filename, response=response, statement=statement)

    else:
        statement='Allowed image types are -> png, jpg, jpeg'
        return render_template('index.html', statement=statement)


@app.route('/display/<filename>')
def display(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/display_result_image/<filename>')
def display_result_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='result/' + filename), code=301)


@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(port=5001)