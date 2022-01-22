import os
import threading
import uuid

from flask import Flask, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename

import gcode
from pixz import save_file
from sensors import Sensors

UPLOAD_FOLDER = './temp_images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

sensors = Sensors()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/convert", methods=["POST"])
def convert_image():
    if 'file' not in request.files:
        return jsonify({"error": "no_file_part"}), 400
    if 'brightness' not in request.values.keys():
        brightness = 0
    else:
        brightness = int(request.values.get('brightness'))

    if 'contrast' not in request.values.keys():
        contrast = 0
    else:
        contrast = float(request.values.get('contrast'))

    if 'size' not in request.values.keys():
        size = None
    else:
        size = int(request.values.get('size'))
        size = (size, size)

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "file_not_found"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        original = uuid.uuid4().hex+"-"+filename
        path = os.path.join(app.config["UPLOAD_FOLDER"], original)
        print("Uploading file "+path)
        file.save(path)

        converted_name = uuid.uuid4().hex
        save_file(file=path,
                  brightness=brightness,
                  contrast=contrast,
                  path=os.path.join(app.config["UPLOAD_FOLDER"], converted_name+".png"),
                  size=size)

        return jsonify({"original": url_for("download_file", name=original),
                        "converted": url_for("download_file", name=converted_name+".png"),
                        "id": converted_name})
    return jsonify({"error": "file_format_not_allowed"}), 400


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


gc = gcode.GCode()


@app.route('/api/start', methods=['POST'])
def start():
    if gc.status is not gcode.Status.IDLE:
        return jsonify({"error": "already_running"}), 400
    if "id" not in request.values.keys():
        return jsonify({"error": "missing_id_parameter"}), 400
    file = os.path.join(app.config["UPLOAD_FOLDER"], request.values.get("id")+".png")
    if not os.path.isfile(file):
        return jsonify({"error": "file_not_found"}), 404
    port = "COM12"
    if "port" in request.values.keys():
        port = request.values.get("port")
    gc.image = request.values.get("id")
    thread = threading.Thread(target=gc.parse_image, args=[file, port])
    thread.start()

    return jsonify({"status": "started"})


@app.route('/')
def main_page():
    return send_from_directory("static", "index.html")


@app.route('/api/kill', methods=["POST"])
def kill():
    if gc.connected:
        gc.kill()
        return jsonify({"status": "killed"})
    return jsonify({"status": "not_connected"})


@app.route('/api/status')
def get_status():
    return jsonify({"sensors": {
                        "ground": {
                            "temperature": sensors.ground_temperature,
                            "humidity": sensors.ground_humidity
                        },
                        "air": {
                            "temperature": sensors.air_temperature,
                            "humidity": sensors.air_humidity
                        }
                    },
                    "progress": {
                        "x": gc.pixels[0],
                        "y": gc.pixels[1],
                        "percent": round(gc.progress/100, 2)
                    },
                    "status": gc.status.value,
                    "status_code": gc.status.name,
                    "connected": gc.connected,
                    "image": url_for("download_file", name=gc.image+".png")
                    if gc.image is not None else None})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
