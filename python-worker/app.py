from flask import Flask, request, send_file
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)

@app.route("/")
def home():
    return "Python worker running"


@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    input_data = request.files["image"].read()

    output_data = remove(input_data)

    return send_file(
        io.BytesIO(output_data),
        mimetype="image/png"
    )

app.run(host="0.0.0.0", port=8000)