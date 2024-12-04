import requests
import os

SERVER_URL = 'http://localhost:5001'

def upload_calib(calib_path):
    url = f"{SERVER_URL}/upload_calib"
    with open(calib_path, 'rb') as f:
        files = {'calib': f}
        response = requests.post(url, files=files)
        print(response.json())

def upload_frame(frame_path):
    url = f"{SERVER_URL}/upload_frame"
    with open(frame_path, 'rb') as f:
        files = {'frame': f}
        response = requests.post(url, files=files)
        print(response.json())

def droid_slam():
    url = f"{SERVER_URL}/process"
    response = requests.post(url)
    print(response.json())

def detect_people():
    url = f"{SERVER_URL}/detect_people"
    response = requests.post(url)
    print(response.json())

def poses_and_coordinates():
    url = f"{SERVER_URL}/poses_and_coordinates"
    response = requests.post(url)
    print(response.json())

def create_spheres():
    url = f"{SERVER_URL}/create_spheres"
    response = requests.post(url)
    print(response.json())    

def download_file(file_url, save_path):
    response = requests.get(file_url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def cleanup_server():
    url = f"{SERVER_URL}/cleanup"
    response = requests.post(url)
    print(response.json())

if __name__ == '__main__':
    calib_path = 'calib.txt'
    frames_folder = 'frames'
    save_dir = 'results'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    upload_calib(calib_path)

    for frame_file in sorted(os.listdir(frames_folder)):
        frame_path = os.path.join(frames_folder, frame_file)
        upload_frame(frame_path)

    droid_slam()
    detect_people()
    poses_and_coordinates()
    create_spheres()

    points_save_path = os.path.join(save_dir, 'points.ply')
    camera_save_path = os.path.join(save_dir, 'camera.ply')
    spheres_save_path = os.path.join(save_dir, 'spheres.ply')

    download_file(f"{SERVER_URL}/download_points", points_save_path)
    download_file(f"{SERVER_URL}/download_camera", camera_save_path)
    download_file(f"{SERVER_URL}/download_spheres", spheres_save_path)
    
    cleanup_server()
