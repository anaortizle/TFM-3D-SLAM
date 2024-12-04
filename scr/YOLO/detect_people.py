import os
from ultralytics import YOLO
import numpy as np
import cv2

# Cargar el modelo YOLOv8
model = YOLO('yolov8n.pt')

# Directorio de frames
frames_dir = 'tmp/frames'

# Verificar que el directorio de frames exista
if not os.path.exists(frames_dir):
    raise Exception(f"El directorio {frames_dir} no existe.")

# Lista para almacenar los frames donde se detectan personas
frames_with_people = []
coordinates_with_people = []

# Detección de personas con YOLOv8 en el directorio completo usando stream=True
results = model(source=frames_dir, classes=0, stream=True)

# Procesar los resultados
for result in results:
    if len(result.boxes) > 0:
        frame_path = result.path  # Ruta completa del frame
        frame_name = os.path.basename(frame_path)  # Nombre del archivo del frame
        valid_detections = False

        # Procesar las cajas delimitadoras
        for box in result.boxes:
            if box.conf >= 0.8:
                valid_detections = True
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()  # Obtener las coordenadas de la caja
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                coordinates_with_people.append((frame_name, center_x, center_y))
        
        if valid_detections:
            frames_with_people.append(frame_name)

# Guardar los frames y poses donde se detectaron personas en un archivo npz
output_npz_file = os.path.join('tmp', 'coordinates_people.npz')
np.savez(output_npz_file, coordinates=coordinates_with_people, frames=frames_with_people)
