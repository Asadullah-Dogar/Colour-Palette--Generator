import os
from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create the uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_light(hex_color):
    """Determine if a hex color is light or dark."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness > 128

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    palette = None
    error = None
    uploaded_image_url = None

    if request.method == 'POST':
        if 'image' not in request.files:
            error = 'No file uploaded!'
        else:
            file = request.files['image']
            if file.filename == '':
                error = 'No selected file'
            elif file and allowed_file(file.filename):
                try:
                    # Save the uploaded file
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # Store the uploaded image URL
                    uploaded_image_url = url_for('static', filename=f'uploads/{filename}')

                    # Process the image to extract the color palette
                    img = Image.open(filepath).convert('RGB')
                    img_data = np.array(img)
                    pixels = img_data.reshape(-1, 3)
                    unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
                    sorted_colors = sorted(zip(unique_colors, counts), key=lambda x: x[1], reverse=True)[:10]

                    palette = []
                    for color, _ in sorted_colors:
                        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                        palette.append({'rgb': list(color), 'hex': hex_color, 'is_light': is_light(hex_color)})

                except Exception as e:
                    error = str(e)
            else:
                error = 'Unsupported file type!'

    return render_template('index.html', palette=palette, error=error, uploaded_image_url=uploaded_image_url)

if __name__ == '__main__':
    app.run(debug=True)
