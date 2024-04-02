import os
import requests
from flask import Flask, flash, request, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "m4xpl0it"

@app.route('/empty_page')
def empty_page():
    filename = session.get('filename', None)
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return redirect(url_for('index'))

@app.route('/pred_page')
def pred_page():
    pred = session.get('pred_label', None)
    f_name = session.get('filename', None)
    disease_description = get_disease_description(pred)
    return render_template('pred.html', pred=pred, f_name=f_name, disease_description=disease_description)

def get_disease_description(predicted_disease):
    descriptions = {
        'None': 'No tumor detected. You are healthy!',
        'Meningioma': 'Meningiomas are usually noncancerous tumors arising from the layers of tissue covering the brain and spinal cord.',
        'Glioma': 'Gliomas are a type of tumor that occurs in the brain and spinal cord. They can be aggressive and difficult to treat.',
        'Pitutary': 'Pituitary tumors are growths that develop in your pituitary gland. They can affect hormone levels and cause various symptoms.'
    }
    return descriptions.get(predicted_disease, 'Description not available.')

@app.route('/', methods=['POST', 'GET'])
def index():
    try:
        if request.method == 'POST':
            f = request.files['bt_image']
            filename = str(f.filename)

            if filename!='':
                ext = filename.split(".")
                
                if ext[1] in ALLOWED_EXTENSIONS:
                    filename = secure_filename(f.filename)

                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'rb') as img:
                        predicted = requests.post("http://localhost:5000/predict", files={"file": img}).json()

                    session['pred_label'] = predicted['class_name']
                    session['filename'] = filename

                    return redirect(url_for('pred_page'))

    except Exception as e:
        print("Exception\n")
        print(e, '\n')

    return render_template('index.html')

if __name__=="__main__":
    app.run(port=3000)
    