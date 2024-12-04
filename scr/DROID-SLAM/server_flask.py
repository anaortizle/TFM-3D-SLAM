from flask import Flask, request, jsonify, send_file
import os
import subprocess
import shutil

app = Flask(__name__)

BASE_DIR = 'tmp'
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'frames')
CALIB_FILE = os.path.join(BASE_DIR, 'calib.txt')
RESULTS_PATH = os.path.join(BASE_DIR, 'results')
RECONSTRUCTION_PATH = os.path.join(BASE_DIR, 'reconstructions')
POINTS_FILE = os.path.join(RESULTS_PATH, 'points.ply')
CAMERA_FILE = os.path.join(RESULTS_PATH, 'camera.ply')
SPHERES_FILE = os.path.join(RESULTS_PATH, 'spheres.ply')
YOLO_DIR = 'YOLO'

# Crear una función para asegurarse de que los directorios necesarios existen
def ensure_directories_exist():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(RESULTS_PATH):
        os.makedirs(RESULTS_PATH)
    if not os.path.exists(RECONSTRUCTION_PATH):
        os.makedirs(RECONSTRUCTION_PATH)
        
frames = []

@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    ensure_directories_exist()
    file = request.files['frame']
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)
    frames.append(filename)
    return jsonify({"message": "Frame uploaded successfully"}), 200

@app.route('/upload_calib', methods=['POST'])
def upload_calib():
    ensure_directories_exist()
    file = request.files['calib']
    file.save(CALIB_FILE)
    return jsonify({"message": "Calibration file uploaded successfully"}), 200

@app.route('/process', methods=['POST'])
def droid_slam():
    try:
        command = f"python demo.py --imagedir={UPLOAD_FOLDER} --calib={CALIB_FILE} --reconstruction_path=tmp/reconstructions --buffer=2048"
        subprocess.run(command, shell=True, check=True)
        return jsonify({"status": "success", "message": "Processing done"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/detect_people', methods=['POST'])
def detect_people():
    try:
        command = f"python {os.path.join(YOLO_DIR, 'detect_people.py')}"
        subprocess.run(command, shell=True, check=True)
        return jsonify({"status": "success", "message": "People detection done"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/poses_and_coordinates', methods=['POST'])
def poses_and_coordinates():
    try:
        command = f"python {os.path.join(YOLO_DIR, 'poses_and_coordinates.py')}"
        subprocess.run(command, shell=True, check=True)
        return jsonify({"status": "success", "message": "Relation between poses and coordinates done"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/create_spheres', methods=['POST'])
def create_spheres():
    try:
        command = f"python {os.path.join(YOLO_DIR, 'create_spheres.py')}"
        subprocess.run(command, shell=True, check=True)
        return jsonify({"status": "success", "message": "Spheres created"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/download_points', methods=['GET'])
def download_points():
    try:
        return send_file(POINTS_FILE, as_attachment=True)
    finally:
        os.remove(POINTS_FILE)

@app.route('/download_camera', methods=['GET'])
def download_camera():
    try:
        return send_file(CAMERA_FILE, as_attachment=True)
    finally:
        os.remove(CAMERA_FILE)

@app.route('/download_spheres', methods=['GET'])
def download_spheres():
    try:
        return send_file(SPHERES_FILE, as_attachment=True)
    finally:
        os.remove(SPHERES_FILE)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        # Eliminar todo lo que se encuentra en el directorio 'tmp'
        if os.path.exists(BASE_DIR):
            shutil.rmtree(BASE_DIR)
        
        return jsonify({"status": "success", "message": "Temporary files deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
