from flask import Flask, request, send_file, jsoni, render_template
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')        
@app.route('/remove-bg', methods=['POST'])
def remove_background():
    try:
        # Kontrola či prišla fotka
        if 'image' not in request.files:
            return jsonify({'error': 'Žiadna fotka nebola nahraná'}), 400
        
        image_file = request.files['image']
        
        # Otvorenie obrázka
        img = Image.open(image_file.stream)
        
        # REMBG spracovanie - odstránenie pozadia
        output = remove(img)
        
        # Vytvorenie bieleho pozadia (aby to nebolo priesvitné)
        white_bg = Image.new('RGB', output.size, (255, 255, 255))
        
        # Spojenie upravenej fotky s bielym pozadím
        if output.mode == 'RGBA':
            white_bg.paste(output, mask=output.split()[3])  # Alpha kanál ako maska
        else:
            white_bg = output.convert('RGB')
        
        # Zlepšenie kontrastu
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(white_bg)
        final_image = enhancer.enhance(1.2)
        
        # Uloženie do BytesIO
        img_io = io.BytesIO()
        final_image.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
    
    except Exception as e:
        return jsonify({'error': f'Chyba pri spracovaní: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
