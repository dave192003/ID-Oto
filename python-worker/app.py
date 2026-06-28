from flask import Flask, request, send_file
from rembg import remove
from PIL import Image
import cv2
import numpy as np
import io

app = Flask(__name__)

@app.route("/")
def home():
    return "Python worker running"


@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    if "image" not in request.files:
        return "Missing image file", 400

    print("REMOVE BG HIT")
    input_data = request.files["image"].read()

    # 1. Alisin ang background gamit ang rembg (magiging transparent PNG muna ito)
    output_transparent_bytes = remove(input_data)

    # 2. I-convert ang bytes papunta sa isang Pillow Image object
    img_transparent = Image.open(io.BytesIO(output_transparent_bytes)).convert("RGBA")

    # 3. Gumawa ng solid white background canvas na may kaparehong sukat (width, height)
    white_background = Image.new("RGBA", img_transparent.size, (255, 255, 255, 255))

    # 4. I-paste ang transparent image sa ibabaw ng puting canvas
    final_img = Image.alpha_composite(white_background, img_transparent)

    # 5. I-save bilang JPEG
    output = io.BytesIO()
    final_img.convert("RGB").save(output, format="JPEG", quality=95)
    output.seek(0)

    print("REMOVE BG DONE (WHITE BG)")

    return send_file(
        output,
        mimetype="image/jpeg"
    )


@app.route("/id-crop", methods=["POST"])
def id_crop():
    if "image" not in request.files:
        return "Missing image file", 400

    print("ID CROP HIT")
    file = request.files["image"].read()

    # Basahin via OpenCV para sa mabilis at madaling array padding manipulation
    np_img = np.frombuffer(file, np.uint8)
    img_bgr = cv2.imdecode(np_img, cv2.IMREAD_UNCHANGED)

    if img_bgr is None:
        return "Invalid image file", 400

    # Siguraduhing 3 channels (RGB) para sa haarcascade processing
    if len(img_bgr.shape) == 3 and img_bgr.shape[2] == 4:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGRA2RGB)
    else:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    if len(faces) == 0:
        return "No face detected", 400

    # Piliin ang pinakamalaking mukha kung sakaling may background clutter
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    x, y, w, h = faces[0]

    # ---------------------------------------------------
    # MAS DESIGNED ZOOM-IN ID PHOTO CROP (PERFECT 1:1)
    # ---------------------------------------------------
    img_h, img_w = img_rgb.shape[:2]
    
    # Ginawang 1.9 mula 2.8 para maging mas tight at zoom-in ang focus sa mukha
    img_h, img_w = img_rgb.shape[:2]
    
    # GINAWANG 2.3: Sakto lang ang zoom, may leeg at tamang taas ng balikat
    crop_size = int(w * 2.3) 

    center_x = x + w // 2
    center_y = y + h // 2

    # Kalkulahin ang target coordinates
    left = center_x - crop_size // 2
    
    # Ginawang 0.40 para maganda ang bagsak ng framing sa ulo at balikat
    top = center_y - int(crop_size * 0.40)  
    right = left + crop_size
    bottom = top + crop_size
    # Alamin kung may lumampas ba sa orihinal na gilid ng litrato
    pad_left = max(0, -left)
    pad_top = max(0, -top)
    pad_right = max(0, right - img_w)
    pad_bottom = max(0, bottom - img_h)

    # I-crop lamang ang ligtas at pasok na rehiyon
    cropped_rgb = img_rgb[max(0, top):min(img_h, bottom), max(0, left):min(img_w, right)]

    # Kung lumampas sa gilid (hal. sagad ang ulo sa itaas), lagyan ito ng WHITE PADDING
    if pad_left > 0 or pad_top > 0 or pad_right > 0 or pad_bottom > 0:
        cropped_rgb = cv2.copyMakeBorder(
            cropped_rgb, pad_top, pad_bottom, pad_left, pad_right, 
            borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )

    # I-convert pabalik sa Pillow para sa pinal na resize at pag-save
    pil_cropped = Image.fromarray(cropped_rgb)
    final_cropped = pil_cropped.resize((600, 600), Image.Resampling.LANCZOS)

    output = io.BytesIO()
    final_cropped.save(output, format="PNG")
    output.seek(0)

    print("ID CROP DONE")

    return send_file(
        output,
        mimetype="image/png"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)