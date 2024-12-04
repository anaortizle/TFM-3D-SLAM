import numpy as np
import os

# Cargar los datos
coordinates_data = np.load('tmp/coordinates_people.npz')
traj_est = np.load('tmp/reconstructions/traj_est.npy')

# Extraer las coordenadas y los nombres de los frames
coordinates = coordinates_data['coordinates.npy']
frames = coordinates_data['frames.npy']

# Crear arrays para almacenar los datos combinados
frames_list = []
xs_list = []
ys_list = []
poses_list = []

# Asociar cada detección con la pose correspondiente
for entry in coordinates:
    frame_name = entry[0]  # Nombre del frame
    x = float(entry[1])    # Coordenada x
    y = float(entry[2])    # Coordenada y
    
    # Obtener el índice del frame
    frame_index = int(frame_name.split('.')[0])

    if frame_index % 3 == 0:
        traj_index = frame_index // 3  # Aplicar el stride

        if traj_index < len(traj_est):
            # Añadir los datos a las listas
            frames_list.append(frame_name)
            xs_list.append(x)
            ys_list.append(y)
            poses_list.append(traj_est[traj_index])

# Convertir listas a arrays
frames_array = np.array(frames_list)
xs_array = np.array(xs_list)
ys_array = np.array(ys_list)
poses_array = np.array(poses_list)

# Ruta donde se guardará el archivo
output_dir = 'tmp'
output_path = os.path.join(output_dir, 'poses_and_coordinates.npz')

# Guardar los datos combinados en un archivo .npz
np.savez(output_path, frames=frames_array, xs=xs_array, ys=ys_array, poses=poses_array)

print("Archivo poses_and_coordinates.npz creado con éxito.")
