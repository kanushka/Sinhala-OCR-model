# @author: BLK Gayan
# @purpose: Upload file for recognize Sinhala text and give basic WEb view

import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from logging.config import dictConfig

from google.cloud import storage
from google.cloud.storage import Blob

import sinhalaocr

UPLOAD_FOLDER = '\\uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Instantiates a client
storage_client = storage.Client()

# The name for the new bucket
bucket_name = 'gayan-new-bucket'
bucket = storage_client.get_bucket(bucket_name)
print('Bucket {} selected.'.format(bucket.name))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            file.save('uploads/' + filename)
            app.logger.info('%s file uploaded successfully', filename)
            
            # save in gcloud bucket
            destination_blob_name = 'uploads/' + filename
            source_file_name = 'uploads/' + filename
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_file_name)
            print('Blob file {} uploaded to {}.'.format(
                source_file_name,
                destination_blob_name))

            # get sinhala text form uploaded image
            # text = sinhalaocr.convert_to_sinhala_text(blob.download_to_filename(filename))
            text = sinhalaocr.convert_to_sinhala_text('uploads/' + filename)

            # remove file
            os.remove('uploads/' + filename)
            app.logger.info('%s file removed', filename)

            # remove file in gcloud
            blob.delete()
            print('Blob {} deleted.'.format(destination_blob_name))

            return render_template('upload-success.html', filename=filename, text=text)

    return render_template('upload.html')

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)