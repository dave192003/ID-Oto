from flask import Flask, request, send_file
from rembg import remove
from PIL import Image, ImageOps
import cv2
import numpy as np
import io

app = Flask(__name__)

DPI = 300   # print quality

# PHOTO CONFIGURATION (actual print size @300dpi)
PHOTO_TYPES = {
    "1x1": {
        "width": 300,
        "height": 300,
        "crop_ratio": 1.0
    },

    "1.5x1.5": {
        "width": 450,
        "height": 450,
        "crop_ratio": 1.0
    },

    "2x2": {
        "width": 600,
        "height": 600,
        "crop_ratio": 1.0
    },

    # 35mm x 45mm
    "passport": {
        "width": 413,
        "height": 531,
        "crop_ratio": 35 / 45
    }
}


@app.route("/")
def home():
    return "Python worker running"


# ==========================
# REMOVE BACKGROUND
# ==========================
@app.route("/remove-bg", methods=["POST"])
def remove_bg():

    if "image" not in request.files:
        return "Missing image file", 400

    print("REMOVE BG HIT")

    input_data = request.files["image"].read()

    output_transparent_bytes = remove(input_data)

    img_transparent = Image.open(
        io.BytesIO(output_transparent_bytes)
    ).convert("RGBA")

    white_background = Image.new(
        "RGBA",
        img_transparent.size,
        (255, 255, 255, 255)
    )

    final_img = Image.alpha_composite(
        white_background,
        img_transparent
    )

    output = io.BytesIO()

    final_img.convert("RGB").save(
        output,
        format="JPEG",
        quality=95,
        dpi=(DPI, DPI)
    )

    output.seek(0)

    print("REMOVE BG DONE")

    return send_file(
        output,
        mimetype="image/jpeg"
    )


# ==========================
# ID CROP
# ==========================
@app.route("/id-crop", methods=["POST"])
def id_crop():

    if "image" not in request.files:
        return "Missing image file", 400

    photo_type = request.form.get("type")

    if photo_type not in PHOTO_TYPES:
        return "Invalid photo type", 400

    print("ID CROP HIT")
    print("TYPE:", photo_type)

    config = PHOTO_TYPES[photo_type]
    crop_ratio = config["crop_ratio"]

    file = request.files["image"].read()

    np_img = np.frombuffer(file, np.uint8)

    img_bgr = cv2.imdecode(
        np_img,
        cv2.IMREAD_UNCHANGED
    )

    if img_bgr is None:
        return "Invalid image file", 400

    # force RGB
    if len(img_bgr.shape) == 3 and img_bgr.shape[2] == 4:
        img_rgb = cv2.cvtColor(
            img_bgr,
            cv2.COLOR_BGRA2RGB
        )
    else:
        img_rgb = cv2.cvtColor(
            img_bgr,
            cv2.COLOR_BGR2RGB
        )

    gray = cv2.cvtColor(
        img_rgb,
        cv2.COLOR_RGB2GRAY
    )

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray,
        1.1,
        5
    )

    if len(faces) == 0:
        return "No face detected", 400

    # biggest face
    faces = sorted(
        faces,
        key=lambda f: f[2] * f[3],
        reverse=True
    )

    x, y, w, h = faces[0]

    img_h, img_w = img_rgb.shape[:2]

    # crop calculations
    if crop_ratio == 1.0:
        crop_width = int(w * 2.3)
        crop_height = crop_width
    else:
        crop_height = int(h * 3.0)
        crop_width = int(crop_height * crop_ratio)

    center_x = x + w // 2
    center_y = y + h // 2

    left = center_x - crop_width // 2
    top = center_y - int(crop_height * 0.40)

    right = left + crop_width
    bottom = top + crop_height

    pad_left = max(0, -left)
    pad_top = max(0, -top)
    pad_right = max(0, right - img_w)
    pad_bottom = max(0, bottom - img_h)

    cropped_rgb = img_rgb[
        max(0, top):min(img_h, bottom),
        max(0, left):min(img_w, right)
    ]

    if (
        pad_left > 0 or
        pad_top > 0 or
        pad_right > 0 or
        pad_bottom > 0
    ):
        cropped_rgb = cv2.copyMakeBorder(
            cropped_rgb,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            borderType=cv2.BORDER_CONSTANT,
            value=[255, 255, 255]
        )

    pil_cropped = Image.fromarray(cropped_rgb)

    # resize based on actual chosen type
    final_cropped = pil_cropped.resize(
        (config["width"], config["height"]),
        Image.Resampling.LANCZOS
    )

    output = io.BytesIO()

    final_cropped.save(
        output,
        format="PNG",
        dpi=(DPI, DPI)
    )

    output.seek(0)

    print("ID CROP DONE")

    return send_file(
        output,
        mimetype="image/png"
    )


# ==========================
# ENHANCE IMAGE
# ==========================
@app.route("/enhance", methods=["POST"])
def enhance():

    if "image" not in request.files:
        return "Missing image file", 400

    print("ENHANCE HIT")

    file = request.files["image"].read()

    np_img = np.frombuffer(
        file,
        np.uint8
    )

    img = cv2.imdecode(
        np_img,
        cv2.IMREAD_COLOR
    )

    if img is None:
        return "Invalid image", 400

    # denoise
    denoised = cv2.fastNlMeansDenoisingColored(
        img,
        None,
        5,
        5,
        7,
        21
    )

    # sharpen
    kernel = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])

    sharpened = cv2.filter2D(
        denoised,
        -1,
        kernel
    )

    # contrast + brightness
    enhanced = cv2.convertScaleAbs(
        sharpened,
        alpha=1.1,
        beta=8
    )

    # convert to PIL to preserve DPI
    img_rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)

    output = io.BytesIO()

    pil_img.save(
        output,
        format="PNG",
        dpi=(DPI, DPI)
    )

    output.seek(0)

    print("ENHANCE DONE")

    return send_file(
        output,
        mimetype="image/png"
    )




# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000
    )